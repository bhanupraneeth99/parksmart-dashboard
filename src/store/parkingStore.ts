import { create } from 'zustand';
import { Booking, ParkingSlot, User } from '../types/parking';

const BOOKING_DURATION_MS = 15 * 60 * 1000; // 15 minutes

const generateSlots = (): ParkingSlot[] => {
  const slots: ParkingSlot[] = [];
  for (let i = 1; i <= 7; i++) {
    slots.push({
      id: `S${i}`,
      number: `S-0${i}`,
      floor: 'S',
      status: Math.random() > 0.6 ? 'occupied' : 'available',
    });
  }
  return slots;
};

interface ParkingStore {
  currentUser: User | null;
  slots: ParkingSlot[];
  bookings: Booking[];
  login: (email: string, password: string, role: 'user' | 'admin') => boolean;
  logout: () => void;
  register: (name: string, email: string, password: string) => boolean;
  addBooking: (data: Omit<Booking, 'id' | 'bookingTime' | 'expiryTime' | 'status'>) => Booking;
  cancelBooking: (bookingId: string) => void;
  expireBooking: (bookingId: string) => void;
}

const mockSlots = generateSlots();
// Set a few as reserved for demo
mockSlots[1].status = 'reserved';
mockSlots[4].status = 'reserved';

const mockAdminUser: User = { id: 'admin-1', name: 'Admin', email: 'admin@park.com', role: 'admin' };

export const useParkingStore = create<ParkingStore>((set, get) => ({
  currentUser: null,
  slots: mockSlots,
  bookings: [
    {
      id: 'b1',
      customerName: 'John Smith',
      phone: '555-0101',
      vehicleNumber: 'ABC-1234',
      slotId: 'S2',
      slotNumber: 'S-02',
      bookingTime: new Date(Date.now() - 5 * 60 * 1000),
      expiryTime: new Date(Date.now() + 10 * 60 * 1000),
      status: 'active',
    },
    {
      id: 'b2',
      customerName: 'Jane Doe',
      phone: '555-0202',
      vehicleNumber: 'XYZ-5678',
      slotId: 'S5',
      slotNumber: 'S-05',
      bookingTime: new Date(Date.now() - 20 * 60 * 1000),
      expiryTime: new Date(Date.now() - 5 * 60 * 1000),
      status: 'expired',
    },
  ],

  login: (email, _password, role) => {
    if (role === 'admin' && email === 'admin@park.com') {
      set({ currentUser: mockAdminUser });
      return true;
    }
    if (role === 'user' && email) {
      set({
        currentUser: {
          id: `user-${Date.now()}`,
          name: email.split('@')[0],
          email,
          role: 'user',
        },
      });
      return true;
    }
    return false;
  },

  logout: () => set({ currentUser: null }),

  register: (name, email, _password) => {
    set({
      currentUser: { id: `user-${Date.now()}`, name, email, role: 'user' },
    });
    return true;
  },

  addBooking: (data) => {
    const now = new Date();
    const booking: Booking = {
      ...data,
      id: `b-${Date.now()}`,
      bookingTime: now,
      expiryTime: new Date(now.getTime() + BOOKING_DURATION_MS),
      status: 'active',
    };
    set((state) => ({
      bookings: [...state.bookings, booking],
      slots: state.slots.map((s) =>
        s.id === data.slotId ? { ...s, status: 'reserved' } : s
      ),
    }));
    return booking;
  },

  cancelBooking: (bookingId) => {
    const booking = get().bookings.find((b) => b.id === bookingId);
    if (!booking) return;
    set((state) => ({
      bookings: state.bookings.map((b) =>
        b.id === bookingId ? { ...b, status: 'cancelled' } : b
      ),
      slots: state.slots.map((s) =>
        s.id === booking.slotId ? { ...s, status: 'available' } : s
      ),
    }));
  },

  expireBooking: (bookingId) => {
    const booking = get().bookings.find((b) => b.id === bookingId);
    if (!booking) return;
    set((state) => ({
      bookings: state.bookings.map((b) =>
        b.id === bookingId ? { ...b, status: 'expired' } : b
      ),
      slots: state.slots.map((s) =>
        s.id === booking.slotId ? { ...s, status: 'available' } : s
      ),
    }));
  },
}));
