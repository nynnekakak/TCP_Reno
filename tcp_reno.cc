// =============================================================
// File: scratch/tcp-reno-project/tcp-reno-enhanced.cc
// Simulate TCP Reno with DropTail vs RED Queue Comparison
// 7-node topology with detailed FSM tracing
// Compatible with ns-3.43
// All outputs saved to results/ directory
// =============================================================

#include <iomanip>
#include <fstream>
#include <map>
#include <string>
#include <cstdlib>
#include <unistd.h>
#include <ctime>
#include <sstream>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/tcp-header.h"
#include "ns3/tcp-socket-base.h"
#include "ns3/tcp-congestion-ops.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/traffic-control-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("TcpRenoSimulation");

// =============================================================
// Global variables
// =============================================================
static std::ofstream g_cwndStream;
static std::ofstream g_stateStream;
static std::ofstream g_summaryStream;

static uint32_t g_ssthresh = 0xFFFFFFFF;
static uint32_t g_prevCwnd = 0;
static uint32_t g_lastAckNum = 0;
static uint32_t g_consecutiveDupAcks = 0;
static bool g_inFastRecovery = false;
static std::string g_currentState = "SlowStart";

// Statistics counters
static uint32_t g_totalStateChanges = 0;
static uint32_t g_totalDupAcks = 0;
static uint32_t g_totalTimeouts = 0;
static uint32_t g_totalFastRetransmits = 0;
static uint32_t g_totalFastRecoveries = 0;

// =============================================================
// Helper: log event to console + file
// =============================================================
static void
LogEvent(const std::string &tag, const std::string &detail = "")
{
  double now = Simulator::Now().GetSeconds();
  std::ostringstream oss;
  oss << std::fixed << std::setprecision(3) << now;
  std::string times = oss.str();

  std::cout << times << "s: [" << tag << "]";
  if (!detail.empty()) std::cout << " " << detail;
  std::cout << std::endl;

  if (g_stateStream.is_open())
  {
    g_stateStream << std::left << std::setw(8) << times
                  << std::setw(20) << tag;
    if (!detail.empty()) g_stateStream << detail;
    g_stateStream << std::endl;
    g_stateStream.flush();
  }

  usleep(10000);
}

// =============================================================
// FSM: state change helper
// =============================================================
static void
ChangeState(const std::string &newState, const std::string &reason)
{
  if (newState != g_currentState)
  {
    std::ostringstream oss;
    oss << g_currentState << " -> " << newState << " [Reason: " << reason << "]";
    LogEvent("STATE_CHANGE", oss.str());
    g_currentState = newState;
    g_totalStateChanges++;
  }
}

// =============================================================
// Trace handlers
// =============================================================
static void
TxPacket(Ptr<const Packet> packet, const TcpHeader &header, Ptr<const TcpSocketBase> socket)
{
  if (header.GetFlags() & TcpHeader::SYN)
  {
    LogEvent("TX-SYN", "Seq=" + std::to_string(header.GetSequenceNumber().GetValue()));
  }
  else if (packet->GetSize() > 0)
  {
    LogEvent("TX-DATA", "Seq=" + std::to_string(header.GetSequenceNumber().GetValue()) +
                          " Size=" + std::to_string(packet->GetSize()));
  }
}

static void
RxPacket(Ptr<const Packet> packet, const TcpHeader &header, Ptr<const TcpSocketBase> socket)
{
  if (!(header.GetFlags() & TcpHeader::ACK))
    return;

  uint32_t currentAck = header.GetAckNumber().GetValue();

  if (currentAck == g_lastAckNum && currentAck > 0)
  {
    g_consecutiveDupAcks++;
    g_totalDupAcks++;
    LogEvent("DUP_ACK", "Ack=" + std::to_string(currentAck) +
                            " dupCount=" + std::to_string(g_consecutiveDupAcks));

    if (g_consecutiveDupAcks == 3 && !g_inFastRecovery)
    {
      LogEvent("TRIPLE_DUP_ACK", "Detected 3 duplicate ACKs -> Fast Retransmit");
      ChangeState("FastRecovery", "Triple Duplicate ACKs (Fast Retransmit)");

      g_inFastRecovery = true;
      g_ssthresh = g_prevCwnd / 2;
      g_totalFastRetransmits++;
      g_totalFastRecoveries++;
      LogEvent("UPDATE", "ssthresh=" + std::to_string(g_ssthresh));
    }
    else if (g_consecutiveDupAcks > 3 && g_inFastRecovery)
    {
      LogEvent("FAST_RECOVERY_DUP", "Still in Fast Recovery, Ack=" + std::to_string(currentAck));
    }
    return;
  }

  if (currentAck > g_lastAckNum)
  {
    g_lastAckNum = currentAck;
    LogEvent("NEW_ACK", "Ack=" + std::to_string(currentAck));

    if (g_inFastRecovery)
    {
      LogEvent("EXIT_FAST_RECOVERY", "New ACK received, leaving Fast Recovery");
      g_inFastRecovery = false;
      g_consecutiveDupAcks = 0;
      ChangeState("CongestionAvoidance", "Recovery complete (new ACK)");
    }
    else
    {
      g_consecutiveDupAcks = 0;
    }
  }
}

static void
SsthreshChange(uint32_t oldSsthresh, uint32_t newSsthresh)
{
  std::ostringstream oss;
  oss << "old=" << oldSsthresh << " new=" << newSsthresh;

  if (g_consecutiveDupAcks >= 3)
  {
    LogEvent("SSTHRESH_UPDATE", oss.str() + " [Cause: Triple Duplicate ACK]");
  }
  else
  {
    LogEvent("SSTHRESH_UPDATE", oss.str() + " [Cause: Timeout]");
  }

  g_ssthresh = newSsthresh;
}

static void
CwndChange(uint32_t oldCwnd, uint32_t newCwnd)
{
  double now = Simulator::Now().GetSeconds();

  if (g_currentState == "SlowStart" && newCwnd >= g_ssthresh)
  {
    ChangeState("CongestionAvoidance", "cwnd >= ssthresh");
    g_consecutiveDupAcks = 0;
  }

  if (g_cwndStream.is_open())
  {
    g_cwndStream << std::fixed << std::setprecision(6)
                 << now << " " << (double)newCwnd / 1024.0 << std::endl;
    g_cwndStream.flush();
  }

  g_prevCwnd = newCwnd;
}

static void
RtoChange(Time oldRto, Time newRto)
{
  std::ostringstream oss;
  oss << "oldRTO=" << oldRto.GetSeconds() << "s newRTO=" << newRto.GetSeconds() << "s";
  LogEvent("RTO_CHANGE", oss.str());

  if (newRto > oldRto * 1.5)
  {
    LogEvent("TIMEOUT_EVENT", "RTO backoff -> Timeout retransmission");
    g_ssthresh = g_prevCwnd / 2;
    g_consecutiveDupAcks = 0;
    g_inFastRecovery = false;
    g_totalTimeouts++;

    if (g_currentState == "CongestionAvoidance" || g_currentState == "FastRecovery")
    {
      ChangeState("SlowStart", "Timeout event (packet loss)");
    }
    else if (g_currentState == "SlowStart")
    {
      LogEvent("TIMEOUT_IN_SS", "Remain in SlowStart but reset cwnd/dupACK");
    }
  }
}

// =============================================================
// Tracing setup
// =============================================================
static void
SetupTracing(Ptr<Application> app)
{
  Ptr<BulkSendApplication> bulkApp = DynamicCast<BulkSendApplication>(app);
  if (!bulkApp) return;

  Ptr<Socket> socket = bulkApp->GetSocket();
  Ptr<TcpSocketBase> tcpSocket = DynamicCast<TcpSocketBase>(socket);
  if (!tcpSocket) return;

  tcpSocket->TraceConnectWithoutContext("CongestionWindow", MakeCallback(&CwndChange));
  tcpSocket->TraceConnectWithoutContext("SlowStartThreshold", MakeCallback(&SsthreshChange));
  tcpSocket->TraceConnectWithoutContext("Tx", MakeCallback(&TxPacket));
  tcpSocket->TraceConnectWithoutContext("Rx", MakeCallback(&RxPacket));
  tcpSocket->TraceConnectWithoutContext("RTO", MakeCallback(&RtoChange));

  LogEvent("TRACE_SETUP", "Connected TcpSocketBase traces");
}

// =============================================================
// Main
// =============================================================
int main(int argc, char *argv[])
{
  // Default parameters
  std::string queueType = "DropTail";
  double duration = 20.0;
  uint32_t numFlows = 3;
  
  // Buffer sizes
  uint32_t s_buf_size = 131072;
  uint32_t r_buf_size = 131072;
  
  // TCP parameters
  uint32_t cwnd = 1;
  uint32_t ssthresh = 65535;
  uint32_t mtu = 1500;
  bool sack = true;
  bool nagle = false;
  double error_p = 0.0;
  
  // Link parameters
  std::string s_bandwidth = "10Mbps";
  std::string s_delay = "5ms";
  std::string r_bandwidth = "10Mbps";
  std::string r_delay = "5ms";
  std::string bottleneck_bandwidth = "5Mbps";
  std::string bottleneck_delay = "10ms";
  
  // Queue parameters
  uint32_t tcp_queue_size = 25;
  
  // Simulation parameters
  uint32_t run = 0;
  uint32_t max_mbytes_to_send = 0;
  std::string prefix_file_name = "P2P-project";
  std::string graph_output = "png";
  bool ascii_tracing = false;
  bool pcap_tracing = false;

  CommandLine cmd;
  cmd.AddValue("queueType", "Queue type: DropTail or RED", queueType);
  cmd.AddValue("duration", "Duration of the simulation (s)", duration);
  cmd.AddValue("numFlows", "Number of flows to simulate (1-3)", numFlows);
  
  cmd.AddValue("s_buf_size", "Sender buffer size (bytes)", s_buf_size);
  cmd.AddValue("r_buf_size", "Receiver buffer size (bytes)", r_buf_size);
  
  cmd.AddValue("cwnd", "Initial congestion window (segments)", cwnd);
  cmd.AddValue("ssthresh", "Initial slow start threshold (segments)", ssthresh);
  cmd.AddValue("mtu", "Size of IP packets to send (bytes)", mtu);
  cmd.AddValue("sack", "Enable SACK", sack);
  cmd.AddValue("nagle", "Enable Nagle algorithm", nagle);
  cmd.AddValue("error_p", "Packet error rate", error_p);
  
  cmd.AddValue("s_bandwidth", "Sender link bandwidth", s_bandwidth);
  cmd.AddValue("s_delay", "Sender link delay", s_delay);
  cmd.AddValue("r_bandwidth", "Receiver link bandwidth", r_bandwidth);
  cmd.AddValue("r_delay", "Receiver link delay", r_delay);
  cmd.AddValue("bottleneck_bandwidth", "Bottleneck link bandwidth", bottleneck_bandwidth);
  cmd.AddValue("bottleneck_delay", "Bottleneck link delay", bottleneck_delay);
  
  cmd.AddValue("tcp_queue_size", "TCP queue size (packets)", tcp_queue_size);
  cmd.AddValue("run", "Run id", run);
  cmd.AddValue("max_mbytes_to_send", "Maximum number of megabytes to send (MB)", max_mbytes_to_send);
  cmd.AddValue("prefix_file_name", "Prefix file name", prefix_file_name);
  cmd.AddValue("graph_output", "The type of image to output: png, svg", graph_output);
  cmd.AddValue("ascii_tracing", "Enable ASCII tracing", ascii_tracing);
  cmd.AddValue("pcap_tracing", "Enable Pcap tracing", pcap_tracing);
  
  cmd.Parse(argc, argv);

  // Validate number of flows
  if (numFlows < 1 || numFlows > 3)
  {
    std::cerr << "Error: numFlows must be between 1 and 3" << std::endl;
    return 1;
  }

  // Create results directory if it doesn't exist
  std::string resultsDir = "scratch/tcp_reno_project/results/";
  system(("mkdir -p " + resultsDir).c_str());

  // Set RNG run number
  RngSeedManager::SetRun(run);

  // Generate timestamp for unique filenames
  std::time_t now = std::time(nullptr);
  std::tm* localTime = std::localtime(&now);
  std::ostringstream timestamp;
  timestamp << std::setfill('0') 
            << std::setw(4) << (localTime->tm_year + 1900)
            << std::setw(2) << (localTime->tm_mon + 1)
            << std::setw(2) << localTime->tm_mday << "_"
            << std::setw(2) << localTime->tm_hour
            << std::setw(2) << localTime->tm_min
            << std::setw(2) << localTime->tm_sec;
  
  std::string unique_prefix = prefix_file_name + "_" + timestamp.str();
  
  std::string cwndFile = resultsDir + unique_prefix + "_cwnd_trace_" + queueType + ".tr";
  std::string stateFile = resultsDir + unique_prefix + "_tcp_state_" + queueType + ".log";
  std::string summaryFile = resultsDir + unique_prefix + "_summary_" + queueType + ".txt";

  g_cwndStream.open(cwndFile);
  g_stateStream.open(stateFile);
  g_summaryStream.open(summaryFile);

  g_stateStream << "# time      EVENT                DETAILS\n";
  g_stateStream << "---------------------------------------------\n";

  // =============================================================
  // Topology: 7 nodes
  // 3 senders (n0, n1, n2) -> 1 router (n3) -> 1 bottleneck router (n4) -> 2 receivers (n5, n6)
  // =============================================================
  NodeContainer senders;
  senders.Create(3);  // n0, n1, n2

  NodeContainer routers;
  routers.Create(2);  // n3 (aggregation), n4 (bottleneck)

  NodeContainer receivers;
  receivers.Create(2);  // n5, n6

  // Senders -> Router n3
  PointToPointHelper p2pAccess;
  p2pAccess.SetDeviceAttribute("DataRate", StringValue(s_bandwidth));
  p2pAccess.SetChannelAttribute("Delay", StringValue(s_delay));
  p2pAccess.SetQueue("ns3::DropTailQueue<Packet>", "MaxSize", StringValue(std::to_string(tcp_queue_size * 2) + "p"));

  NetDeviceContainer devS0R3 = p2pAccess.Install(senders.Get(0), routers.Get(0));
  NetDeviceContainer devS1R3 = p2pAccess.Install(senders.Get(1), routers.Get(0));
  NetDeviceContainer devS2R3 = p2pAccess.Install(senders.Get(2), routers.Get(0));

  // Router n3 -> Router n4 (BOTTLENECK with queue discipline)
  PointToPointHelper p2pBottleneck;
  p2pBottleneck.SetDeviceAttribute("DataRate", StringValue(bottleneck_bandwidth));
  p2pBottleneck.SetChannelAttribute("Delay", StringValue(bottleneck_delay));
  p2pBottleneck.SetQueue("ns3::DropTailQueue<Packet>", "MaxSize", StringValue("1p")); // Minimal for QDisc

  NetDeviceContainer devR3R4 = p2pBottleneck.Install(routers.Get(0), routers.Get(1));

  // Router n4 -> Receivers
  PointToPointHelper p2pEgress;
  p2pEgress.SetDeviceAttribute("DataRate", StringValue(r_bandwidth));
  p2pEgress.SetChannelAttribute("Delay", StringValue(r_delay));
  p2pEgress.SetQueue("ns3::DropTailQueue<Packet>", "MaxSize", StringValue(std::to_string(tcp_queue_size * 2) + "p"));

  NetDeviceContainer devR4R5 = p2pEgress.Install(routers.Get(1), receivers.Get(0));
  NetDeviceContainer devR4R6 = p2pEgress.Install(routers.Get(1), receivers.Get(1));

  // Add error model if requested
  if (error_p > 0.0)
  {
    Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
    em->SetAttribute("ErrorRate", DoubleValue(error_p));
    devR3R4.Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(em));
    LogEvent("ERROR_MODEL", "Packet error rate set to " + std::to_string(error_p));
  }

  // Install Internet Stack
  InternetStackHelper stack;
  stack.Install(senders);
  stack.Install(routers);
  stack.Install(receivers);

  // Install Traffic Control on bottleneck link
  TrafficControlHelper tch;
  if (queueType == "RED")
  {
    tch.SetRootQueueDisc("ns3::RedQueueDisc",
                         "MaxSize", QueueSizeValue(QueueSize(std::to_string(tcp_queue_size) + "p")),
                         "MinTh", DoubleValue(tcp_queue_size * 0.2),
                         "MaxTh", DoubleValue(tcp_queue_size * 0.6),
                         "MeanPktSize", UintegerValue(mtu),
                         "Wait", BooleanValue(true),
                         "Gentle", BooleanValue(true),
                         "LinkBandwidth", DataRateValue(DataRate(bottleneck_bandwidth)),
                         "LinkDelay", TimeValue(MilliSeconds(10)));
    LogEvent("QUEUE_SETUP", "Using RED Queue Discipline on bottleneck");
  }
  else
  {
    tch.SetRootQueueDisc("ns3::FifoQueueDisc", "MaxSize", QueueSizeValue(QueueSize(std::to_string(tcp_queue_size) + "p")));
    LogEvent("QUEUE_SETUP", "Using DropTail (FIFO) Queue Discipline on bottleneck");
  }
  tch.Install(devR3R4.Get(0)); // Install on router n3's interface to n4

  // Assign IP addresses
  Ipv4AddressHelper address;
  
  address.SetBase("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer ifS0R3 = address.Assign(devS0R3);
  
  address.SetBase("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer ifS1R3 = address.Assign(devS1R3);
  
  address.SetBase("10.1.3.0", "255.255.255.0");
  Ipv4InterfaceContainer ifS2R3 = address.Assign(devS2R3);
  
  address.SetBase("10.1.4.0", "255.255.255.0");
  Ipv4InterfaceContainer ifR3R4 = address.Assign(devR3R4);
  
  address.SetBase("10.1.5.0", "255.255.255.0");
  Ipv4InterfaceContainer ifR4R5 = address.Assign(devR4R5);
  
  address.SetBase("10.1.6.0", "255.255.255.0");
  Ipv4InterfaceContainer ifR4R6 = address.Assign(devR4R6);

  // Enable routing
  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  // TCP configuration
  Config::SetDefault("ns3::TcpL4Protocol::SocketType", TypeIdValue(TcpNewReno::GetTypeId()));
  Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue(mtu - 40)); // MTU - IP/TCP headers
  Config::SetDefault("ns3::TcpSocket::InitialCwnd", UintegerValue(cwnd));
  Config::SetDefault("ns3::TcpSocket::DelAckCount", UintegerValue(1));
  Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue(s_buf_size));
  Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue(r_buf_size));
  Config::SetDefault("ns3::TcpSocketBase::Sack", BooleanValue(sack));
  
  if (ssthresh < 65535)
  {
    Config::SetDefault("ns3::TcpSocket::InitialSlowStartThreshold", UintegerValue(ssthresh * (mtu - 40)));
  }

  // Setup applications
  uint16_t port = 8080;
  ApplicationContainer serverApps, clientApps;

  // Calculate max bytes to send
  uint64_t maxBytes = (max_mbytes_to_send == 0) ? 0 : max_mbytes_to_send * 1024 * 1024;

  // Receiver 0 (n5)
  Address serverAddr0(InetSocketAddress(ifR4R5.GetAddress(1), port));
  PacketSinkHelper sink0("ns3::TcpSocketFactory", serverAddr0);
  ApplicationContainer serverApp0 = sink0.Install(receivers.Get(0));
  serverApp0.Start(Seconds(0.0));
  serverApp0.Stop(Seconds(duration + 1.0));
  serverApps.Add(serverApp0);

  // Receiver 1 (n6)
  Address serverAddr1(InetSocketAddress(ifR4R6.GetAddress(1), port + 1));
  PacketSinkHelper sink1("ns3::TcpSocketFactory", serverAddr1);
  ApplicationContainer serverApp1 = sink1.Install(receivers.Get(1));
  serverApp1.Start(Seconds(0.0));
  serverApp1.Stop(Seconds(duration + 1.0));
  serverApps.Add(serverApp1);

  // Flow 1: Sender 0 -> Receiver 0
  if (numFlows >= 1)
  {
    BulkSendHelper source0("ns3::TcpSocketFactory", serverAddr0);
    source0.SetAttribute("MaxBytes", UintegerValue(maxBytes));
    source0.SetAttribute("SendSize", UintegerValue(mtu - 40));
    ApplicationContainer clientApp0 = source0.Install(senders.Get(0));
    clientApp0.Start(Seconds(1.0));
    clientApp0.Stop(Seconds(duration + 0.5));
    clientApps.Add(clientApp0);
    
    // Setup tracing for first sender
    Simulator::Schedule(Seconds(1.1), &SetupTracing, clientApp0.Get(0));
  }

  // Flow 2: Sender 1 -> Receiver 1
  if (numFlows >= 2)
  {
    BulkSendHelper source1("ns3::TcpSocketFactory", serverAddr1);
    source1.SetAttribute("MaxBytes", UintegerValue(maxBytes));
    source1.SetAttribute("SendSize", UintegerValue(mtu - 40));
    ApplicationContainer clientApp1 = source1.Install(senders.Get(1));
    clientApp1.Start(Seconds(2.0));
    clientApp1.Stop(Seconds(duration + 0.5));
    clientApps.Add(clientApp1);
  }

  // Flow 3: Sender 2 -> Receiver 0 (competing traffic)
  if (numFlows >= 3)
  {
    BulkSendHelper source2("ns3::TcpSocketFactory", serverAddr0);
    source2.SetAttribute("MaxBytes", UintegerValue(maxBytes));
    source2.SetAttribute("SendSize", UintegerValue(mtu - 40));
    ApplicationContainer clientApp2 = source2.Install(senders.Get(2));
    clientApp2.Start(Seconds(3.0));
    clientApp2.Stop(Seconds(duration + 0.5));
    clientApps.Add(clientApp2);
  }

  // Enable tracing if requested
  if (ascii_tracing)
  {
    AsciiTraceHelper ascii;
    p2pBottleneck.EnableAsciiAll(ascii.CreateFileStream(resultsDir + unique_prefix + "_ascii.tr"));
    LogEvent("ASCII_TRACING", "Enabled");
  }

  if (pcap_tracing)
  {
    p2pBottleneck.EnablePcapAll(resultsDir + unique_prefix + "_pcap", false);
    LogEvent("PCAP_TRACING", "Enabled");
  }

  // Flow Monitor
  FlowMonitorHelper flowmon;
  Ptr<FlowMonitor> monitor = flowmon.InstallAll();

  // Launch realtime plotter (optional)
 if (numFlows >= 1) {
    pid_t pid = fork();
    if (pid == 0) // Child process
    {
        // Construct the full path to the Python script
        std::string scriptPath = "scratch/tcp_reno_project/plot_realtime.py";
        
        // Pass the cwnd trace file name as an argument to the python script
        // Note: The python script will need to know the full path to the cwnd trace file.
        // It's safer to provide the absolute path or a path relative to where `waf` is run.
        // Assuming `waf` is run from the ns-3 root directory.
        std::string fullCwndFilePath = cwndFile; 
        
        // Execute the python script
        execlp("python3", "python3", scriptPath.c_str(), fullCwndFilePath.c_str(), (char *)nullptr);
        
        // If execlp fails
        perror("execlp failed");
        _exit(1); // Exit with an error code
    }
  }

  Simulator::Stop(Seconds(duration + 1.0));
  
  std::cout << "\n========================================\n";
  std::cout << "SIMULATION CONFIGURATION\n";
  std::cout << "========================================\n";
  std::cout << "Queue Type: " << queueType << "\n";
  std::cout << "Duration: " << duration << " seconds\n";
  std::cout << "Number of Flows: " << numFlows << "\n";
  std::cout << "MTU: " << mtu << " bytes\n";
  std::cout << "Initial CWND: " << cwnd << " segments\n";
  std::cout << "Initial SSThresh: " << ssthresh << " segments\n";
  std::cout << "SACK: " << (sack ? "Enabled" : "Disabled") << "\n";
  std::cout << "Nagle: " << (nagle ? "Enabled" : "Disabled") << "\n";
  std::cout << "Error Rate: " << error_p << "\n";
  std::cout << "Sender Bandwidth: " << s_bandwidth << "\n";
  std::cout << "Bottleneck Bandwidth: " << bottleneck_bandwidth << "\n";
  std::cout << "Queue Size: " << tcp_queue_size << " packets\n";
  std::cout << "========================================\n\n";
  
  Simulator::Run();

  // =============================================================
  // Generate Summary Report
  // =============================================================
  monitor->CheckForLostPackets();
  Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
  auto stats = monitor->GetFlowStats();

  std::cout << "\n========================================\n";
  std::cout << "SIMULATION SUMMARY (" << queueType << " Queue)\n";
  std::cout << "========================================\n";

  g_summaryStream << "========================================\n";
  g_summaryStream << "SIMULATION SUMMARY (" << queueType << " Queue)\n";
  g_summaryStream << "========================================\n\n";

  g_summaryStream << "Simulation Configuration:\n";
  g_summaryStream << "  - Duration: " << duration << " seconds\n";
  g_summaryStream << "  - Number of Flows: " << numFlows << "\n";
  g_summaryStream << "  - MTU: " << mtu << " bytes\n";
  g_summaryStream << "  - Initial CWND: " << cwnd << " segments\n";
  g_summaryStream << "  - Initial SSThresh: " << ssthresh << " segments\n";
  g_summaryStream << "  - SACK: " << (sack ? "Enabled" : "Disabled") << "\n";
  g_summaryStream << "  - Error Rate: " << error_p << "\n\n";

  g_summaryStream << "Network Topology:\n";
  g_summaryStream << "  - 3 Senders (n0, n1, n2)\n";
  g_summaryStream << "  - 2 Routers (n3: aggregation, n4: bottleneck)\n";
  g_summaryStream << "  - 2 Receivers (n5, n6)\n";
  g_summaryStream << "  - Sender Links: " << s_bandwidth << ", " << s_delay << " delay\n";
  g_summaryStream << "  - Bottleneck Link: " << bottleneck_bandwidth << ", " << bottleneck_delay << " delay\n";
  g_summaryStream << "  - Receiver Links: " << r_bandwidth << ", " << r_delay << " delay\n\n";

  double totalThroughput = 0;
  uint32_t totalTxPackets = 0;
  uint32_t totalRxPackets = 0;
  uint32_t totalLostPackets = 0;
  double totalDelay = 0;
  uint32_t flowCount = 0;

  for (auto &kv : stats)
  {
    Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(kv.first);
    double throughput = (kv.second.rxBytes * 8.0 / duration / 1e6);
    double avgDelay = (kv.second.rxPackets > 0) ? 
                      (kv.second.delaySum.GetSeconds() / kv.second.rxPackets * 1000.0) : 0;
    uint32_t lostPackets = kv.second.txPackets - kv.second.rxPackets;
    double lossRate = (kv.second.txPackets > 0) ? 
                      (100.0 * lostPackets / kv.second.txPackets) : 0;

    std::cout << "Flow " << kv.first << " (" << t.sourceAddress << " -> " 
              << t.destinationAddress << ")\n";
    std::cout << "  Tx Packets: " << kv.second.txPackets << "\n";
    std::cout << "  Rx Packets: " << kv.second.rxPackets << "\n";
    std::cout << "  Lost Packets: " << lostPackets << " (" << std::fixed 
              << std::setprecision(2) << lossRate << "%)\n";
    std::cout << "  Throughput: " << std::fixed << std::setprecision(3) 
              << throughput << " Mbps\n";
    std::cout << "  Avg Delay: " << std::fixed << std::setprecision(2) 
              << avgDelay << " ms\n";
    std::cout << "--------------------------------------\n";

    g_summaryStream << "Flow " << kv.first << " (" << t.sourceAddress << " -> " 
                    << t.destinationAddress << ")\n";
    g_summaryStream << "  Tx Packets: " << kv.second.txPackets << "\n";
    g_summaryStream << "  Rx Packets: " << kv.second.rxPackets << "\n";
    g_summaryStream << "  Lost Packets: " << lostPackets << " (" << std::fixed 
                    << std::setprecision(2) << lossRate << "%)\n";
    g_summaryStream << "  Throughput: " << std::fixed << std::setprecision(3) 
                    << throughput << " Mbps\n";
    g_summaryStream << "  Avg Delay: " << std::fixed << std::setprecision(2) 
                    << avgDelay << " ms\n";
    g_summaryStream << "--------------------------------------\n";

    totalThroughput += throughput;
    totalTxPackets += kv.second.txPackets;
    totalRxPackets += kv.second.rxPackets;
    totalLostPackets += lostPackets;
    totalDelay += avgDelay;
    flowCount++;
  }

  double avgThroughput = (flowCount > 0) ? (totalThroughput / flowCount) : 0;
  double avgDelay = (flowCount > 0) ? (totalDelay / flowCount) : 0;
  double overallLossRate = (totalTxPackets > 0) ? 
                           (100.0 * totalLostPackets / totalTxPackets) : 0;

  std::cout << "\nAGGREGATE STATISTICS:\n";
  std::cout << "  Total Throughput: " << std::fixed << std::setprecision(3) 
            << totalThroughput << " Mbps\n";
  std::cout << "  Average Throughput per Flow: " << avgThroughput << " Mbps\n";
  std::cout << "  Total Packets Sent: " << totalTxPackets << "\n";
  std::cout << "  Total Packets Received: " << totalRxPackets << "\n";
  std::cout << "  Total Lost Packets: " << totalLostPackets 
            << " (" << std::setprecision(2) << overallLossRate << "%)\n";
  std::cout << "  Average Delay: " << avgDelay << " ms\n";

  std::cout << "\nTCP STATE MACHINE STATISTICS:\n";
  std::cout << "  Total State Changes: " << g_totalStateChanges << "\n";
  std::cout << "  Total Duplicate ACKs: " << g_totalDupAcks << "\n";
  std::cout << "  Total Fast Retransmits: " << g_totalFastRetransmits << "\n";
  std::cout << "  Total Fast Recoveries: " << g_totalFastRecoveries << "\n";
  std::cout << "  Total Timeouts: " << g_totalTimeouts << "\n";

  g_summaryStream << "\nAGGREGATE STATISTICS:\n";
  g_summaryStream << "  Total Throughput: " << std::fixed << std::setprecision(3) 
                  << totalThroughput << " Mbps\n";
  g_summaryStream << "  Average Throughput per Flow: " << avgThroughput << " Mbps\n";
  g_summaryStream << "  Total Packets Sent: " << totalTxPackets << "\n";
  g_summaryStream << "  Total Packets Received: " << totalRxPackets << "\n";
  g_summaryStream << "  Total Lost Packets: " << totalLostPackets 
                  << " (" << std::setprecision(2) << overallLossRate << "%)\n";
  g_summaryStream << "  Average Delay: " << avgDelay << " ms\n";

  g_summaryStream << "\nTCP STATE MACHINE STATISTICS:\n";
  g_summaryStream << "  Total State Changes: " << g_totalStateChanges << "\n";
  g_summaryStream << "  Total Duplicate ACKs: " << g_totalDupAcks << "\n";
  g_summaryStream << "  Total Fast Retransmits: " << g_totalFastRetransmits << "\n";
  g_summaryStream << "  Total Fast Recoveries: " << g_totalFastRecoveries << "\n";
  g_summaryStream << "  Total Timeouts: " << g_totalTimeouts << "\n";

  g_summaryStream << "\n========================================\n";
  g_summaryStream << "KEY OBSERVATIONS:\n";
  g_summaryStream << "========================================\n";
  if (queueType == "RED")
  {
    g_summaryStream << "RED queue provides early congestion signaling through\n";
    g_summaryStream << "probabilistic packet drops, which should result in:\n";
    g_summaryStream << "  - More evenly distributed packet losses\n";
    g_summaryStream << "  - Better flow fairness\n";
    g_summaryStream << "  - Reduced queueing delay\n";
    g_summaryStream << "  - Smoother throughput variations\n";
  }
  else
  {
    g_summaryStream << "DropTail queue uses tail-drop policy, which typically:\n";
    g_summaryStream << "  - Causes bursty packet losses\n";
    g_summaryStream << "  - May lead to global synchronization\n";
    g_summaryStream << "  - Higher queueing delay during congestion\n";
    g_summaryStream << "  - More aggressive retransmission patterns\n";
  }

  Simulator::Destroy();

  g_cwndStream.close();
  g_stateStream.close();
  g_summaryStream.close();

  std::cout << "\n========================================\n";
  std::cout << "Files generated:\n";
  std::cout << "  - " << cwndFile << "\n";
  std::cout << "  - " << stateFile << "\n";
  std::cout << "  - " << summaryFile << "\n";
  std::cout << "========================================\n\n";

  return 0;
}
