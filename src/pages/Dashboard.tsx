import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MessageCircle, Trophy, Upload, BarChart3, LogOut } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface DashboardStats {
  total: number;
  allocated: number;
  garage: number;
  due_service: number;
  spare_ready: number;
  reserved: number;
  written_off: number;
}

interface MetricCard {
  label: string;
  key: keyof DashboardStats;
  status?: string;
  color: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('User');

  useEffect(() => {
    fetchVehicleSummary();
    const userData = sessionStorage.getItem('user_data');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        setUserName(user.name || 'User');
      } catch (e) {
        console.error('Failed to parse user data:', e);
      }
    }
  }, []);

  const fetchVehicleSummary = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/dashboard/vehicle-summary');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch vehicle summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('user_session');
    sessionStorage.removeItem('user_data');
    navigate('/login');
  };

  const metrics: MetricCard[] = [
    { label: 'Total Vehicles', key: 'total', color: 'bg-blue-500' },
    { label: 'Allocated', key: 'allocated', status: 'Allocated', color: 'bg-green-500' },
    { label: 'In Garage', key: 'garage', status: 'Garage', color: 'bg-orange-500' },
    { label: 'Due for Service', key: 'due_service', status: 'Due_Service', color: 'bg-red-500' },
    { label: 'Spare Ready', key: 'spare_ready', status: 'Spare_Ready', color: 'bg-purple-500' },
    { label: 'Reserved', key: 'reserved', status: 'Reserved', color: 'bg-yellow-500' },
    { label: 'Written Off', key: 'written_off', status: 'Written_Off', color: 'bg-gray-500' },
  ];

  const navigationButtons = [
    {
      icon: MessageCircle,
      label: 'Chat with AI',
      description: 'Ask questions about your fleet',
      color: 'from-blue-500 to-blue-600',
      onClick: () => navigate('/chatbot'),
    },
    {
      icon: Trophy,
      label: 'Driving Scores',
      description: 'Engineer performance metrics',
      color: 'from-yellow-500 to-yellow-600',
      onClick: () => navigate('/webfleet'),
    },
    {
      icon: Upload,
      label: 'Upload Vehicles',
      description: 'Add or update vehicle data',
      color: 'from-green-500 to-green-600',
      onClick: () => navigate('/upload'),
    },
    {
      icon: BarChart3,
      label: 'Assets Gallery',
      description: 'View all fleet vehicles',
      color: 'from-purple-500 to-purple-600',
      onClick: () => navigate('/assets'),
    },
  ];

  const handleCardClick = (metric: MetricCard) => {
    if (metric.status) {
      navigate(`/assets?status=${encodeURIComponent(metric.status)}`);
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fleet Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {userName}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <LogOut size={20} />
          Sign Out
        </button>
      </div>

      {/* Quick Access Buttons */}
      <div className="mb-12">
        <h2 className="text-lg font-bold mb-4">⚡ Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {navigationButtons.map((button, index) => {
            const Icon = button.icon;
            return (
              <button
                key={index}
                onClick={button.onClick}
                className="group relative overflow-hidden rounded-lg p-4 text-left transition-all duration-300 hover:scale-105"
              >
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${button.color} transition-all duration-300 group-hover:shadow-lg`}
                />
                <div className="absolute inset-0 bg-black/10 group-hover:bg-black/5 transition-all" />
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-2">
                    <Icon size={24} className="text-white" />
                    <h3 className="text-sm font-bold text-white">{button.label}</h3>
                  </div>
                  <p className="text-white/80 text-xs">{button.description}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Vehicle Statistics */}
      <div>
        <h2 className="text-lg font-bold mb-4">📊 Fleet Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric) => (
            <div
              key={metric.key}
              onClick={() => handleCardClick(metric)}
              className={`cursor-pointer transition-transform hover:scale-105 ${
                metric.status ? 'cursor-pointer' : ''
              }`}
            >
              <Card className="h-full hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    {metric.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-end gap-2">
                    <div className={`${metric.color} text-white rounded-full p-3 flex-shrink-0`}>
                      <svg
                        className="w-6 h-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">
                        {stats?.[metric.key] ?? (loading ? '...' : 0)}
                      </div>
                      {metric.status && (
                        <p className="text-xs text-gray-500 mt-1">Click to view</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
