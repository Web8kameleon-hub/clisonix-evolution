/**
 * Layer 16: Validation Layer
 * Input validation and sanitization
 */

import { z, ZodSchema, ZodError } from "zod";
import { Request, Response, NextFunction } from "express";

// ═══════════════════════════════════════════════════════════════════════════════
// COMMON VALIDATION SCHEMAS
// ═══════════════════════════════════════════════════════════════════════════════

export const schemas = {
  // User schemas
  email: z.string().email("Invalid email format"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  username: z
    .string()
    .min(3)
    .max(50)
    .regex(/^[a-zA-Z0-9_]+$/),

  // ID schemas
  uuid: z.string().uuid("Invalid UUID format"),
  id: z.union([z.string(), z.number()]),

  // Pagination
  pagination: z.object({
    page: z.number().int().positive().default(1),
    limit: z.number().int().min(1).max(100).default(20),
    sort: z.string().optional(),
    order: z.enum(["asc", "desc"]).default("desc"),
  }),

  // API request
  apiRequest: z.object({
    message: z.string().min(1).max(10000),
    context: z.record(z.any()).optional(),
    language: z.string().length(2).optional(),
  }),

  // Date range
  dateRange: z.object({
    from: z.string().datetime().or(z.date()),
    to: z.string().datetime().or(z.date()),
  }),
};

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION MIDDLEWARE FACTORY
// ═══════════════════════════════════════════════════════════════════════════════

type ValidationTarget = "body" | "query" | "params";

export function validate<T>(
  schema: ZodSchema<T>,
  target: ValidationTarget = "body",
) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const data =
        target === "body"
          ? req.body
          : target === "query"
            ? req.query
            : req.params;

      const validated = schema.parse(data);

      // Attach validated data to request
      (req as any).validated = validated;

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({
          error: "Validation Error",
          details: error.errors.map((e) => ({
            path: e.path.join("."),
            message: e.message,
          })),
        });
      }
      next(error);
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SANITIZATION HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

export const sanitize = {
  // Remove HTML tags
  stripHtml: (input: string): string => {
    return input.replace(/<[^>]*>/g, "");
  },

  // Escape special characters
  escapeHtml: (input: string): string => {
    const map: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return input.replace(/[&<>"']/g, (m) => map[m]);
  },

  // Trim and normalize whitespace
  normalizeWhitespace: (input: string): string => {
    return input.trim().replace(/\s+/g, " ");
  },

  // Remove null bytes
  removeNullBytes: (input: string): string => {
    return input.replace(/\0/g, "");
  },

  // Full sanitization pipeline
  full: (input: string): string => {
    return sanitize.removeNullBytes(
      sanitize.normalizeWhitespace(sanitize.stripHtml(input)),
    );
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// PREDEFINED VALIDATORS
// ═══════════════════════════════════════════════════════════════════════════════

export const validators = {
  createUser: validate(
    z.object({
      email: schemas.email,
      password: schemas.password,
      username: schemas.username,
    }),
  ),

  chatRequest: validate(schemas.apiRequest),

  paginatedQuery: validate(schemas.pagination, "query"),

  idParam: validate(z.object({ id: schemas.uuid }), "params"),
};

export default {
  schemas,
  validate,
  sanitize,
  validators,
};
