import { pgTable, serial, text, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import type { AgentRun } from "../types/agents.js";

export const installations = pgTable("installations", {
  id: serial("id").primaryKey(),
  githubInstallId: integer("github_install_id").notNull().unique(),
  accountLogin: text("account_login").notNull(),
  accountType: text("account_type").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const repositories = pgTable("repositories", {
  id: serial("id").primaryKey(),
  installationId: integer("installation_id")
    .references(() => installations.id)
    .notNull(),
  fullName: text("full_name").notNull().unique(),
  config: jsonb("config"),
  active: boolean("active").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const jobs = pgTable("jobs", {
  id: serial("id").primaryKey(),
  repositoryId: integer("repository_id")
    .references(() => repositories.id)
    .notNull(),
  sourcePrNumber: integer("source_pr_number").notNull(),
  status: text("status", { enum: ["pending", "running", "completed", "failed"] })
    .default("pending")
    .notNull(),
  agentRuns: jsonb("agent_runs").$type<AgentRun[]>(),
  docPrNumber: integer("doc_pr_number"),
  error: text("error"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  completedAt: timestamp("completed_at"),
});

export type Installation = typeof installations.$inferSelect;
export type Repository = typeof repositories.$inferSelect;
export type Job = typeof jobs.$inferSelect;
