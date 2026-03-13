export type SlotStatus = 'available' | 'reserved' | 'occupied';
export type UserRole = 'user' | 'admin';

export interface ParkingSlot {
  id: string;
  number: string;
  status: SlotStatus;
  floor: string;
  polygon?: string;
  polygon_configured?: boolean;
  heatmap_count?: number;
}

export interface Booking {
  id: string;
  name: string;
  phone: string;
  vehicle_number: string;
  slot_id: string;
  booking_time: string;
  expiry_time: string;
  status: 'active' | 'expired' | 'cancelled' | 'occupied';
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}
