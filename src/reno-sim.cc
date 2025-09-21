/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * TCP Reno Simulation with TraceMetrics Analysis
 * 
 * This program simulates TCP Reno congestion control algorithm using ns-3
 * and generates trace files for analysis with TraceMetrics tool.
 * 
 * Network topology:
 *   n0 ---------- n1 ---------- n2
 *      10 Mbps       1 Mbps
 *      1ms           10ms
 *
 * TCP flow from n0 to n2 through bottleneck link (n1-n2)
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/tcp-header.h"
#include "ns3/internet-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("TcpRenoSimulation");

// Global variables for tracing
std::ofstream cwndFile;
std::ofstream rttFile;
std::ofstream throughputFile;

// Callback functions for tracing
static void
CwndTrace (uint32_t nodeId, uint32_t oldCwnd, uint32_t newCwnd)
{
  cwndFile << Simulator::Now ().GetSeconds () << "\t" << nodeId << "\t" 
           << oldCwnd << "\t" << newCwnd << std::endl;
}

static void
RttTrace (uint32_t nodeId, Time oldRtt, Time newRtt)
{
  rttFile << Simulator::Now ().GetSeconds () << "\t" << nodeId << "\t"
          << oldRtt.GetMilliSeconds () << "\t" << newRtt.GetMilliSeconds () << std::endl;
}

static void
RxTrace (Ptr<const Packet> packet, const Address &address)
{
  static uint64_t totalBytes = 0;
  static Time lastTime = Seconds (0);
  
  totalBytes += packet->GetSize ();
  Time currentTime = Simulator::Now ();
  
  if (currentTime - lastTime >= Seconds (0.1)) // Calculate throughput every 100ms
    {
      double throughput = (totalBytes * 8.0) / (currentTime - lastTime).GetSeconds () / 1000000; // Mbps
      throughputFile << currentTime.GetSeconds () << "\t" << throughput << std::endl;
      lastTime = currentTime;
      totalBytes = 0;
    }
}

int
main (int argc, char *argv[])
{
  // Command line parameters
  uint32_t maxBytes = 0; // 0 means unlimited
  double simulationTime = 20.0; // seconds
  std::string tcpVariant = "TcpNewReno";
  bool tracing = true;
  
  CommandLine cmd;
  cmd.AddValue ("maxBytes", "Total number of bytes to send", maxBytes);
  cmd.AddValue ("simTime", "Simulation time in seconds", simulationTime);
  cmd.AddValue ("tcpVariant", "TCP variant (TcpNewReno, TcpReno, etc.)", tcpVariant);
  cmd.AddValue ("tracing", "Enable tracing", tracing);
  cmd.Parse (argc, argv);

  // Set TCP variant
  if (tcpVariant.compare ("TcpNewReno") == 0)
    {
      Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpNewReno::GetTypeId ()));
    }
  else if (tcpVariant.compare ("TcpReno") == 0)
    {
      Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpReno::GetTypeId ()));
    }

  // Create nodes
  NodeContainer nodes;
  nodes.Create (3);

  // Create point-to-point links
  PointToPointHelper p2p1, p2p2;
  
  // High-speed link: n0 to n1
  p2p1.SetDeviceAttribute ("DataRate", StringValue ("10Mbps"));
  p2p1.SetChannelAttribute ("Delay", StringValue ("1ms"));
  
  // Bottleneck link: n1 to n2
  p2p2.SetDeviceAttribute ("DataRate", StringValue ("1Mbps"));
  p2p2.SetChannelAttribute ("Delay", StringValue ("10ms"));

  NetDeviceContainer devices1, devices2;
  devices1 = p2p1.Install (nodes.Get (0), nodes.Get (1));
  devices2 = p2p2.Install (nodes.Get (1), nodes.Get (2));

  // Install Internet stack
  InternetStackHelper internet;
  internet.Install (nodes);

  // Assign IP addresses
  Ipv4AddressHelper address;
  
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces1 = address.Assign (devices1);
  
  address.SetBase ("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces2 = address.Assign (devices2);

  // Setup routing
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  // Create applications
  uint16_t port = 9;

  // Sink application on node 2
  PacketSinkHelper sinkHelper ("ns3::TcpSocketFactory",
                               InetSocketAddress (Ipv4Address::GetAny (), port));
  ApplicationContainer sinkApp = sinkHelper.Install (nodes.Get (2));
  sinkApp.Start (Seconds (0.0));
  sinkApp.Stop (Seconds (simulationTime));

  // Source application on node 0
  BulkSendHelper sourceHelper ("ns3::TcpSocketFactory",
                               InetSocketAddress (interfaces2.GetAddress (1), port));
  sourceHelper.SetAttribute ("MaxBytes", UintegerValue (maxBytes));
  ApplicationContainer sourceApp = sourceHelper.Install (nodes.Get (0));
  sourceApp.Start (Seconds (1.0));
  sourceApp.Stop (Seconds (simulationTime));

  // Enable tracing if requested
  if (tracing)
    {
      // Open trace files
      cwndFile.open ("results/cwnd-trace.dat");
      rttFile.open ("results/rtt-trace.dat");
      throughputFile.open ("results/throughput-trace.dat");
      
      // Write headers
      cwndFile << "# Time\tNodeId\tOldCwnd\tNewCwnd" << std::endl;
      rttFile << "# Time\tNodeId\tOldRtt\tNewRtt" << std::endl;
      throughputFile << "# Time\tThroughput(Mbps)" << std::endl;

      // Connect trace sources
      Config::ConnectWithoutContext ("/NodeList/0/$ns3::TcpL4Protocol/SocketList/0/CongestionWindow",
                                     MakeBoundCallback (&CwndTrace, 0));
      Config::ConnectWithoutContext ("/NodeList/0/$ns3::TcpL4Protocol/SocketList/0/RTT",
                                     MakeBoundCallback (&RttTrace, 0));
      
      // Connect packet sink receive trace
      Config::ConnectWithoutContext ("/NodeList/2/ApplicationList/0/$ns3::PacketSink/Rx",
                                     MakeCallback (&RxTrace));

      // Enable pcap tracing
      p2p1.EnablePcapAll ("results/reno-sim");
      p2p2.EnablePcapAll ("results/reno-sim");
    }

  NS_LOG_INFO ("Starting simulation...");
  
  // Run simulation
  Simulator::Stop (Seconds (simulationTime));
  Simulator::Run ();
  
  // Close trace files
  if (tracing)
    {
      cwndFile.close ();
      rttFile.close ();
      throughputFile.close ();
    }

  // Calculate and display statistics
  Ptr<PacketSink> sink = DynamicCast<PacketSink> (sinkApp.Get (0));
  std::cout << "Simulation completed successfully!" << std::endl;
  std::cout << "Total Bytes Received: " << sink->GetTotalRx () << std::endl;
  std::cout << "Average Throughput: " << (sink->GetTotalRx () * 8.0) / simulationTime / 1000000 << " Mbps" << std::endl;
  
  Simulator::Destroy ();
  
  NS_LOG_INFO ("Simulation finished.");
  
  return 0;
}