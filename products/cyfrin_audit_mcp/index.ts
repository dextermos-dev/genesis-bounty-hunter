/**
 * Cyfrin Issue #442: Sherlock & Code4rena 27K Findings MCP Server
 * Standard Model Context Protocol (MCP) Server for Smart Contract Security Auditors.
 */

import { z } from "zod";

export const ListVulnerabilityPatternsSchema = z.object({
  protocol_type: z.string().optional().describe("Filter by protocol category (e.g., ERC4626_VAULT, DEX_AMM, LENDING_ORACLE, SOLANA_TOKEN2022)"),
  severity: z.enum(["HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]).optional().describe("Filter by finding severity"),
  search_query: z.string().optional().describe("Keywords to search across finding titles, attack vectors, and tags")
});

export const ScanCodeSchema = z.object({
  source_code: z.string().min(1, "source_code must not be empty").describe("Solidity or Rust source code to analyze against C4/Sherlock patterns")
});

export interface FindingPattern {
  id: string;
  source: "Code4rena" | "Sherlock";
  severity: "HIGH" | "MEDIUM" | "LOW" | "INFORMATIONAL";
  protocol_type: string;
  vulnerability_class: string;
  title: string;
  affected_methods: string[];
  mitigation_pattern: string;
  tags: string[];
}

export type ListVulnerabilityPatternsInput = z.infer<typeof ListVulnerabilityPatternsSchema>;
export type ScanCodeInput = z.infer<typeof ScanCodeSchema>;
