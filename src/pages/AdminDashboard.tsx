import { useNavigate } from 'react-router-dom';
import { useParkingStore } from '@/store/parkingStore';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ParkingGrid } from '@/components/parking/ParkingGrid';
import {
  Car, LogOut, Users, CheckCircle, Clock, AlertCircle,
  Download, BarChart3, TrendingUp, UploadCloud, Video, RefreshCw,
  Play, Square, RotateCcw, Settings2
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

const statusBadge = (status: string) => {
  const map: Record<string, string> = {
    active: 'bg-green-100 text-green-700 border-green-200 hover:bg-green-100',
    expired: 'bg-red-100 text-red-700 border-red-200 hover:bg-red-100',
    cancelled: 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-100',
    occupied: 'bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-100',
  };
  return <Badge className={map[status] || map.cancelled}>{status}</Badge>;
};

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { currentUser, slots, bookings, logout } = useParkingStore();
  const [isUploading, setIsUploading] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState('idle');
  const [apiStats, setApiStats] = useState({ total_slots: 0, available: 0, reserved: 0, occupied: 0 });

  const fetchApiSlots = async () => {
    try {
      await fetch('http://localhost:8000/slots'); // Refresh slot data as requested
      const statsRes = await fetch('http://localhost:8000/slot-stats');
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setApiStats(statsData);
      }
    } catch (e) {
      console.error("Failed to fetch slots from API", e);
    }
  };

  // Fetch analysis status periodically
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:8000/analysis-status');
        if (res.ok) {
          const data = await res.json();
          setAnalysisStatus(data.status);
        }
        await fetchApiSlots();
      } catch (e) {
        console.error("Failed to fetch analysis status", e);
      }
    };
    const interval = setInterval(fetchStatus, 3000);
    fetchStatus(); // Initial fetch
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    console.log("AdminDashboard mounted");
    if (!currentUser || currentUser.role !== 'admin') {
      navigate('/');
    }
  }, [currentUser, navigate]);

  const handleStartAnalysis = async () => {
    await fetch('http://localhost:8000/start-analysis', { method: 'POST' });
    toast.success("Analysis started");
    await fetchApiSlots();
    setAnalysisStatus("processing");
  };

  const handleStopAnalysis = async () => {
    await fetch('http://localhost:8000/stop-analysis', { method: 'POST' });
    toast.warning("Analysis stopped");
    await fetchApiSlots();
    setAnalysisStatus("stopped");
  };

  const handleResetSlots = async () => {
    await fetch('http://localhost:8000/reset-slots', { method: 'POST' });
    toast.success("Parking slots reset to available");
    await fetchApiSlots();
  };

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/upload-parking-video', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        toast.success("Video uploaded successfully. Parking analysis started.");
        setAnalysisStatus('processing');
      } else {
        toast.error("Failed to upload video.");
      }
    } catch (err) {
      toast.error("Network error during upload.");
    } finally {
      setIsUploading(false);
    }
  };

  if (!currentUser || currentUser.role !== 'admin') return null;

  const total = slots.length;
  const available = slots.filter(s => s.status === 'available').length;
  const reserved = slots.filter(s => s.status === 'reserved').length;
  const occupied = slots.filter(s => s.status === 'occupied').length;
  const occupancyRate = Math.round(((occupied + reserved) / total) * 100);

  const downloadCSV = () => {
    const headers = ['Name', 'Phone', 'Vehicle', 'Slot', 'Booking Time', 'Expiry Time', 'Status'];
    const rows = bookings.map(b => [
      b.customerName, b.phone, b.vehicleNumber, b.slotNumber,
      b.bookingTime.toLocaleString(), b.expiryTime.toLocaleString(), b.status,
    ]);
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'bookings.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  const stats = [
    { label: 'Total Slots', value: total, icon: BarChart3, color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200' },
    { label: 'Available', value: available, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50 border-green-200' },
    { label: 'Reserved', value: reserved, icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200' },
    { label: 'Occupied', value: occupied, icon: Car, color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
    { label: 'Occupancy Rate', value: `${occupancyRate}%`, icon: TrendingUp, color: 'text-primary', bg: 'bg-primary/5 border-primary/20' },
    { label: 'Total Bookings', value: bookings.length, icon: Users, color: 'text-purple-600', bg: 'bg-purple-50 border-purple-200' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-card/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--gradient-hero)' }}>
              <Car className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <span className="font-display font-bold text-foreground">ParkSmart</span>
              <span className="text-xs text-muted-foreground ml-2">Admin Dashboard</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="gap-1.5 text-primary border-primary/30 bg-primary/5">
              <AlertCircle className="w-3 h-3" /> Admin
            </Badge>
            <Button variant="outline" size="sm" onClick={() => { logout(); navigate('/'); }} className="gap-2">
              <LogOut className="w-4 h-4" /> Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Stats */}
        <div>
          <h2 className="text-lg font-display font-bold text-foreground mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" /> Analytics Overview
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {stats.map(stat => {
              const Icon = stat.icon;
              return (
                <div key={stat.label} className={`rounded-2xl border p-4 card-shadow ${stat.bg}`}>
                  <Icon className={`w-5 h-5 mb-2 ${stat.color}`} />
                  <p className={`text-2xl font-display font-bold ${stat.color}`}>{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1 font-medium">{stat.label}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Video Upload Section */}
        <section className="bg-card rounded-2xl border border-border p-6 card-shadow flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="text-lg font-display font-bold text-foreground mb-2 flex items-center gap-2">
              <Video className="w-5 h-5 text-primary" /> Parking Video Analysis
            </h2>
            <p className="text-sm text-muted-foreground max-w-xl">
              Upload a <code>.mp4</code> video feed of the parking lot to trigger the YOLOv8 AI detection module.
              The system will automatically process the footage and update slot occupancies.
            </p>
          </div>

          <div className="flex flex-col items-center gap-3 w-full md:w-auto">
            <div className="relative group w-full md:w-auto">
              <Button disabled={isUploading} className="w-full gap-2 bg-primary hover:bg-primary/90 text-primary-foreground">
                {isUploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
                {isUploading ? 'Uploading...' : 'Upload Video File'}
              </Button>
              <input
                type="file"
                accept="video/mp4"
                onChange={handleVideoUpload}
                disabled={isUploading}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
              />
            </div>

            <div className="flex items-center gap-2 text-sm font-medium">
              <span className="text-muted-foreground">Analysis Status:</span>
              {analysisStatus === 'processing' ? (
                <Badge variant="outline" className="text-yellow-600 border-yellow-200 bg-yellow-50 gap-1.5 flex items-center">
                  <RefreshCw className="w-3 h-3 animate-spin" /> Processing
                </Badge>
              ) : analysisStatus === 'completed' ? (
                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 gap-1.5 flex items-center">
                  <CheckCircle className="w-3 h-3" /> Completed
                </Badge>
              ) : analysisStatus === 'error' ? (
                <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50 gap-1.5 flex items-center">
                  <AlertCircle className="w-3 h-3" /> Error
                </Badge>
              ) : (
                <Badge variant="outline" className="text-gray-600 border-gray-200 bg-gray-50 flex items-center">
                  Idle
                </Badge>
              )}
            </div>
          </div>
        </section>

        {/* Parking Analysis Controls */}
        <section className="bg-card rounded-2xl border border-border p-6 card-shadow flex flex-col gap-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-border pb-4">
            <div>
              <h2 className="text-lg font-display font-bold text-foreground flex items-center gap-2">
                <Settings2 className="w-5 h-5 text-primary" /> Parking Analysis Controls
              </h2>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button onClick={handleStartAnalysis} className="gap-2 bg-primary hover:bg-primary/90">
                <Play className="w-4 h-4" /> Start Parking Analysis
              </Button>
              <Button onClick={handleStopAnalysis} variant="outline" className="gap-2 text-yellow-600 border-yellow-200 hover:bg-yellow-50">
                <Square className="w-4 h-4" /> Stop Analysis
              </Button>
              <Button onClick={handleResetSlots} variant="destructive" className="gap-2">
                <RotateCcw className="w-4 h-4" /> Reset Parking Slots
              </Button>
            </div>
          </div>

          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="flex items-center gap-3 bg-muted/30 p-4 rounded-xl border border-border/50">
              <span className="font-semibold text-sm">System Status:</span>
              <Badge
                variant="outline"
                className={`text-sm px-3 py-1 ${analysisStatus === 'processing' ? 'text-green-600 border-green-200 bg-green-50' :
                  analysisStatus === 'stopped' ? 'text-red-600 border-red-200 bg-red-50' :
                    'text-gray-600 border-gray-200 bg-gray-50'
                  }`}
              >
                {analysisStatus === 'processing' ? 'Processing Video / Streaming Detection' :
                  analysisStatus === 'stopped' ? 'Analysis Stopped' : 'Idle'}
              </Badge>
            </div>

            <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-4 w-full">
              <div className="rounded-xl border border-border p-3 bg-card shadow-sm text-center">
                <p className="text-xs text-muted-foreground font-medium mb-1">Total Slots</p>
                <p className="text-xl font-display font-bold text-blue-600">{apiStats.total_slots}</p>
              </div>
              <div className="rounded-xl border border-border p-3 bg-card shadow-sm text-center">
                <p className="text-xs text-muted-foreground font-medium mb-1">Available</p>
                <p className="text-xl font-display font-bold text-green-600">{apiStats.available}</p>
              </div>
              <div className="rounded-xl border border-border p-3 bg-card shadow-sm text-center">
                <p className="text-xs text-muted-foreground font-medium mb-1">Reserved</p>
                <p className="text-xl font-display font-bold text-yellow-600">{apiStats.reserved}</p>
              </div>
              <div className="rounded-xl border border-border p-3 bg-card shadow-sm text-center">
                <p className="text-xs text-muted-foreground font-medium mb-1">Occupied</p>
                <p className="text-xl font-display font-bold text-red-600">{apiStats.occupied}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Live Video Feed */}
        {analysisStatus !== 'idle' && (
          <section className="bg-card rounded-2xl border border-border p-6 card-shadow flex flex-col items-center justify-center">
            <h3 className="font-display font-bold text-foreground mb-4 w-full text-left flex items-center gap-2">
              <Video className="w-5 h-5 text-primary" /> Live Detection Stream
            </h3>
            <div className="w-full max-w-4xl bg-black rounded-lg overflow-hidden flex items-center justify-center min-h-[400px]">
              <img
                src="http://localhost:8000/video-feed"
                alt="Live Parking Feed MJPEG"
                className="w-full max-h-[600px] object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </div>
          </section>
        )}

        {/* Occupancy bar */}
        <div className="bg-card rounded-2xl border border-border p-5 card-shadow">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-display font-semibold text-foreground">Slot Occupancy</h3>
            <span className="text-sm text-muted-foreground">{total} total slots</span>
          </div>
          <div className="w-full h-4 rounded-full overflow-hidden bg-muted flex">
            <div
              className="h-full bg-red-500 transition-all duration-500"
              style={{ width: `${(occupied / total) * 100}%` }}
              title={`Occupied: ${occupied}`}
            />
            <div
              className="h-full bg-yellow-400 transition-all duration-500"
              style={{ width: `${(reserved / total) * 100}%` }}
              title={`Reserved: ${reserved}`}
            />
            <div
              className="h-full bg-green-500 transition-all duration-500"
              style={{ width: `${(available / total) * 100}%` }}
              title={`Available: ${available}`}
            />
          </div>
          <div className="flex gap-6 mt-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Occupied ({occupied})</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-yellow-400" /> Reserved ({reserved})</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-green-500" /> Available ({available})</span>
          </div>
        </div>

        {/* Parking Grid */}
        <section>
          <h2 className="text-lg font-display font-bold text-foreground mb-4 flex items-center gap-2">
            <Car className="w-5 h-5 text-primary" /> Parking Slot Monitor
          </h2>
          <div className="bg-card rounded-2xl border border-border p-6 card-shadow">
            <ParkingGrid slots={slots} />
          </div>
        </section>

        {/* Bookings Table */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-display font-bold text-foreground flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" /> All Bookings
            </h2>
            <Button onClick={downloadCSV} variant="outline" className="gap-2 font-medium">
              <Download className="w-4 h-4" /> Export Excel
            </Button>
          </div>

          <div className="bg-card rounded-2xl border border-border card-shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/50">
                    {['Name', 'Phone', 'Vehicle No.', 'Slot', 'Booking Time', 'Expiry Time', 'Status'].map(h => (
                      <th key={h} className="text-left py-3 px-4 font-semibold text-muted-foreground whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bookings.map((b, i) => (
                    <tr key={b.id} className={`border-b border-border/60 hover:bg-muted/30 transition-colors ${i % 2 === 0 ? '' : 'bg-muted/10'}`}>
                      <td className="py-3 px-4 font-medium text-foreground">{b.customerName}</td>
                      <td className="py-3 px-4 text-muted-foreground">{b.phone}</td>
                      <td className="py-3 px-4 font-mono text-sm font-semibold">{b.vehicleNumber}</td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-1 bg-primary/10 text-primary text-xs font-bold rounded-lg">{b.slotNumber}</span>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground whitespace-nowrap">{b.bookingTime.toLocaleString()}</td>
                      <td className="py-3 px-4 text-muted-foreground whitespace-nowrap">{b.expiryTime.toLocaleString()}</td>
                      <td className="py-3 px-4">{statusBadge(b.status)}</td>
                    </tr>
                  ))}
                  {bookings.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-muted-foreground">No bookings yet</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
