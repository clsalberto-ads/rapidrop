import { z } from "zod";

export const addressSchema = z.object({
  zipcode: z.string().regex(/^\d{5}-?\d{3}$/),
  street: z.string().min(1),
  number: z.string().min(1),
  complement: z.string().optional(),
  neighborhood: z.string().min(1),
  city: z.string().min(1),
  state: z.string().length(2),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
});

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

export const registerMerchantSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  name: z.string().min(2),
  business_name: z.string().min(2),
  document: z.string().min(11).max(18),
  phone: z.string().min(10),
  segment: z.enum(["food", "pharmacy", "grocery"]),
});

export const productSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  price_cents: z.number().int().positive(),
  category_id: z.string().uuid(),
  is_available: z.boolean().default(true),
  unit_type: z.enum(["unit", "kg", "g", "l", "ml", "pack", "dozen"]).default("unit"),
});
