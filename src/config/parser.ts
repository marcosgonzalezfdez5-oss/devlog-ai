import yaml from "js-yaml";
import { DEFAULT_CONFIG, type DevLogAIConfig } from "./defaults.js";

export function parseConfig(raw: string): DevLogAIConfig {
  try {
    const parsed = yaml.load(raw) as Partial<DevLogAIConfig>;
    return { ...DEFAULT_CONFIG, ...parsed };
  } catch {
    return DEFAULT_CONFIG;
  }
}

export function shouldSkipPR(config: DevLogAIConfig, labels: string[], changedFiles: string[]): boolean {
  if (labels.some((l) => config.ignore_labels.includes(l))) return true;
  if (changedFiles.length > 0 && changedFiles.every((f) => matchesAnyPattern(f, config.ignore_paths))) return true;
  return false;
}

function matchesAnyPattern(file: string, patterns: string[]): boolean {
  return patterns.some((pattern) => {
    const regex = new RegExp("^" + pattern.replace(/\./g, "\\.").replace(/\*\*/g, ".*").replace(/\*/g, "[^/]*") + "$");
    return regex.test(file);
  });
}
