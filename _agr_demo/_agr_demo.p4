/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#include "includes/headers.p4"
// #include "includes/registers.p4" // TODO: 能不能移动过去？要定义在 Ingress 里面？

#define JOB_NUM 512                // 支持的聚合 Job 数量

const bit<16> TYPE_IPV4 = 0x800;
const bit<8>  TYPE_ATP = 0x12;
/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_ATP: parse_value;
            default: accept;
        }
    }

    state parse_value {
        packet.extract(hdr.atp);
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr; // NOTE: 也没用了
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1; // NOTE: 没用了
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table drop_table { // NOTE: …… 没办法……
        actions = {
            drop;
        }
        default_action = drop();
    }

    register<bit<5>>(JOB_NUM) count_reg;       // 和 aggregationDegree 同类型
    register<bit<16>>(JOB_NUM) agrValueVector; // NOTE: 暂时不考虑溢出问题。 TODO: int 没有试过，到时候发包解析试试，但是寄存器会遇到问题
    // TODO: 寄存器的命名最好再统一一点。

    action count_read_act() {
        count_reg.read(meta.count_value, (bit<32>)meta.aggIndex);
    }

    table count_read { 
        actions = { 
            count_read_act; 
        }
        default_action = count_read_act();
    }

    action count_add_act() { 
        count_reg.read(meta.count_value, (bit<32>)meta.aggIndex);
        meta.count_value = meta.count_value + 1;
        count_reg.write((bit<32>)meta.aggIndex, meta.count_value);
    }

    table count_add { 
        actions = { 
            count_add_act; 
        }
        default_action = count_add_act();
    }
    
    action count_clean_act() {
        count_reg.write((bit<32>)meta.aggIndex, 0);
    }

    table count_clean {
        actions = {
            count_clean_act;
        }
        default_action = count_clean_act();
    }

    action vector_add_act() { 
        agrValueVector.read(meta.aggre_value, (bit<32>)meta.aggIndex); 
        meta.aggre_value = meta.aggre_value + hdr.atp.value;
        agrValueVector.write((bit<32>)meta.aggIndex, meta.aggre_value);
    }

    table vector_add {      // TODO: 可以不可以直接 acition，不用 table 的？
        actions = { 
            vector_add_act;
        }
        default_action = vector_add_act();
    }

    action vector_read_act() {
        agrValueVector.read(hdr.atp.value, (bit<32>)meta.aggIndex); 
    }

    table vector_read {
        actions = { 
            vector_read_act;
        }
        default_action = vector_read_act();
    }

    apply {
        if(hdr.atp.isValid()) {             // support in-network
            meta.aggIndex = 0;           // TODO: 硬编码，目前还不支持多任务。 应该是根据任务分配的
            count_read.apply();

            vector_add.apply();
            // 根据计数判断
            count_add.apply();
            if((bit<5>)meta.count_value == hdr.atp.aggregationDegree) {
                count_clean.apply();
                vector_read.apply();
                if (hdr.ipv4.isValid()) {
                    ipv4_lpm.apply();
                }
            } else {
                drop_table.apply(); // FIXME: 写得不是很好。
            }
        } else {                            // IPv4
            if (hdr.ipv4.isValid()) {
                ipv4_lpm.apply();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.atp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;