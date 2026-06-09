export enum MerchantSegment {
  FOOD = "food",
  PHARMACY = "pharmacy",
  GROCERY = "grocery",
}

export enum OrderStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  PREPARING = "preparing",
  READY = "ready",
  OUT_FOR_DELIVERY = "out_for_delivery",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
}

export enum PaymentStatus {
  PENDING = "pending",
  APPROVED = "approved",
  DECLINED = "declined",
  REFUNDED = "refunded",
  EXPIRED = "expired",
}

export enum RiderStatus {
  ASSIGNED = "assigned",
  ACCEPTED = "accepted",
  PICKED_UP = "picked_up",
  DELIVERED = "delivered",
}

export enum SubscriptionPhase {
  TRIAL = "trial",
  ACTIVE_PERCENTAGE = "active_percentage",
  ACTIVE_FIXED = "active_fixed",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
}

export enum Channel {
  WHATSAPP = "whatsapp",
  SITE = "site",
  APP = "app",
  MANUAL = "manual",
  PRESENCIAL = "presencial",
}

export interface Address {
  zipcode: string;
  street: string;
  number: string;
  complement?: string;
  neighborhood: string;
  city: string;
  state: string;
  latitude?: number;
  longitude?: number;
}

export interface ProductItem {
  product_id: string;
  product_name: string;
  variation?: string;
  quantity: number;
  unit_price_cents: number;
  total_cents: number;
}
