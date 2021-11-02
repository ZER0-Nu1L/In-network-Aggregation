/*************************************************************************
 ***********************  H E A D E R S  *********************************
 *************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header atp_t {
    bit<32> workerMap;
    bit<5>  aggregationDegree;
    bit<1> overflow;            // TODO: 
    bit<1> isAck;               // TODO: 
    bit<1> ecn;                 // TODO: 
    bit<16> value;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    atp_t        atp;
}


/*************************************************************************
 ***********************  M E T A D A T A  *******************************
 *************************************************************************/

struct metadata { // FIXME: 每次都会清空对吧，这和直接当场定义有什么区别呢
    // 当前处理的 aggIndex，目前还不支持
    bit<8> aggIndex;  // int<8> -x-> bit<32>
    // count 的中间量
    bit<5> count_value; // 最多不超过 aggregationDegree 的大小，类型与之对应 bit<5>
    // value 的中间量
    bit<16> aggre_value; // bit<16>
}