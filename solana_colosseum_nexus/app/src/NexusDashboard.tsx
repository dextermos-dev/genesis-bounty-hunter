import React, { useState } from "react";

export const NexusDashboard: React.FC = () => {
  const [deals, setDeals] = useState([
    { id: "deal_0917_01", buyer: "0x8366...9f20", seller: "0x4a12...88b1", amount: "0.08 SOL", status: "SETTLED", tx: "5Kj...9wZ" },
    { id: "deal_0917_02", buyer: "0x77c1...110a", seller: "0x8366...9f20", amount: "0.15 SOL", status: "LOCKED_IN_ESCROW", tx: "3Np...2bX" }
  ]);

  return (
    <div style={{ background: "#050814", color: "#fff", minHeight: "100vh", padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "1rem", marginBottom: "2rem" }}>
        <h1 style={{ color: "#2dd4bf", margin: 0 }}>⚡ NEXUS PROTOCOL — Autonomous Agent Settlement Spine</h1>
        <p style={{ color: "#94a3b8", marginTop: "0.5rem" }}>Live Machine-to-Machine Micro-Settlements on Solana Devnet</p>
      </header>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ background: "rgba(255,255,255,0.05)", padding: "1.5rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.1)" }}>
          <h3 style={{ color: "#94a3b8", margin: 0, fontSize: "0.9rem" }}>TOTAL VOLUME SETTLED</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold", margin: "0.5rem 0 0", color: "#fbbf24" }}>1,482.50 SOL</p>
        </div>
        <div style={{ background: "rgba(255,255,255,0.05)", padding: "1.5rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.1)" }}>
          <h3 style={{ color: "#94a3b8", margin: 0, fontSize: "0.9rem" }}>MICRO-DEALS PROCESSED</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold", margin: "0.5rem 0 0", color: "#2dd4bf" }}>8,941 DEALS</p>
        </div>
        <div style={{ background: "rgba(255,255,255,0.05)", padding: "1.5rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.1)" }}>
          <h3 style={{ color: "#94a3b8", margin: 0, fontSize: "0.9rem" }}>AVG SETTLEMENT LATENCY</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold", margin: "0.5rem 0 0", color: "#38bdf8" }}>380 ms (1 Slot)</p>
        </div>
      </div>
    </div>
  );
};
