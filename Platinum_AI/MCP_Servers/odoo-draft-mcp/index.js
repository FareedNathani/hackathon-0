#!/usr/bin/env node

/**
 * Odoo Draft-Only MCP Server
 * Connects via XML-RPC (simulated via JSON-RPC for Node simplicity)
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");

// Mock Odoo Client
class OdooClient {
  async createDraftInvoice(partner, amount) {
    console.error(`[Odoo] Creating DRAFT invoice for ${partner}: $${amount}`);
    return { id: Math.floor(Math.random() * 1000), status: "draft" };
  }
}

const odoo = new OdooClient();

const server = new Server(
  {
    name: "odoo-draft-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "create_draft_invoice",
        description: "Creates a DRAFT invoice in Odoo. Does NOT post it.",
        inputSchema: {
          type: "object",
          properties: {
            partner_name: { type: "string" },
            amount: { type: "number" },
          },
          required: ["partner_name", "amount"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "create_draft_invoice") {
    const { partner_name, amount } = request.params.arguments;
    const result = await odoo.createDraftInvoice(partner_name, amount);
    return {
      content: [
        {
          type: "text",
          text: `Created Draft Invoice #${result.id} for ${partner_name}. Status: ${result.status}`,
        },
      ],
    };
  }
  throw new Error("Tool not found");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Odoo Draft MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main loop:", error);
  process.exit(1);
});
