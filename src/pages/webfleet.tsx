import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MainLayout from '@/components/layout/MainLayout';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy, TrendingUp, AlertCircle, CheckCircle, Users, Award } from 'lucide-react';

interface Engineer {
  rank: number;
  name: string;
  email: string;
  van_number: string;
  trade_group: string;
  score: number;
  score_class: string;
}

interface Statistics {
  total_drivers: number;
  drivers_with_scores: number;
  average_score: number;
  highest_score: number;
  excellent: number;
  good: number;
  fair: number;
  needs_improvement: number;
  poor: number;
}

export const Webfleet: React.FC = () => {
  const [engineers, setEngineers] = useState<Engineer[]>([]);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEngineers();
  }, []);

  const isValidName = (name: string): boolean => {
    // LENIENT validation - only reject obvious garbage
    if (!name || name.length < 2) return false;
    
    // Only reject OBVIOUS code/error patterns
    const obviousGarbage = [
      'File "', 'Traceback', 'apply_stylesheet', 'self.archive',
      'from_tree', 'super()', 'cls(**attrib)', '_convert(',
      'expected_type', 'seq = self.container', 'raise TypeError',
      'openpyxl.', '.py", line', '~~~~~~~~^^^', '~~~~~~~~~~~~~~~~^',
      '^^^^^^^^^^', '~~~~~~~~~~~~~~~~~~~~'
    ];
    
    for (const pattern of obviousGarbage) {
      if (name.includes(pattern)) return false;
    }
    
    // Must have at least one letter
    if (!/[a-zA-Z]/.test(name)) return false;
    
    return true;
  };

  const fetchEngineers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('http://localhost:8000/api/drivers/excel');
      
      // Double filtering - frontend protection!
      const cleanDrivers = response.data.drivers
        .filter((driver: any) => isValidName(driver.name))
        .map((driver: any) => ({
          rank: driver.rank,
          name: driver.name,
          email: driver.email || 'N/A',
          van_number: driver.van_number || 'N/A',
          trade_group: driver.trade_group || 'N/A',
          score: driver.score || 0,
          score_class: driver.score_class || 'poor'
        }));
      
      setEngineers(cleanDrivers);
      setStats(response.data.statistics);
      
    } catch (err) {
      console.error('Failed to fetch drivers:', err);
      setError('Failed to load driver data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreBadgeColor = (scoreClass: string) => {
    const colors = {
      excellent: 'bg-green-100 text-green-800 border-green-300',
      good: 'bg-blue-100 text-blue-800 border-blue-300',
      fair: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      needs_improvement: 'bg-orange-100 text-orange-800 border-orange-300',
      poor: 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[scoreClass as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 9.0) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (score >= 8.0) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 7.0) return <TrendingUp className="w-5 h-5 text-blue-600" />;
    return <AlertCircle className="w-5 h-5 text-orange-600" />;
  };

  const getRowColor = (scoreClass: string) => {
    const colors = {
      excellent: 'bg-green-50/50 hover:bg-green-100/50',
      good: 'bg-blue-50/50 hover:bg-blue-100/50',
      fair: 'bg-yellow-50/30 hover:bg-yellow-100/30',
      needs_improvement: 'bg-orange-50/30 hover:bg-orange-100/30',
      poor: 'bg-red-50/30 hover:bg-red-100/30'
    };
    return colors[scoreClass as keyof typeof colors] || 'hover:bg-gray-50';
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Award className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Award className="w-6 h-6 text-orange-600" />;
    return <span className="font-bold text-gray-600">#{rank}</span>;
  };

  return (
    <MainLayout
      title="🚗 Fleet Performance Dashboard"
      subtitle="Real-time driving scores and performance analytics"
    >
      <div className="space-y-6">
        {/* Top Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-blue-700 mb-1">Total Engineers</p>
                  <p className="text-3xl font-bold text-blue-900">{stats.total_drivers}</p>
                </div>
                <Users className="w-12 h-12 text-blue-400 opacity-60" />
              </div>
            </Card>
            
            <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-green-700 mb-1">Average Score</p>
                  <p className="text-3xl font-bold text-green-900">{stats.average_score.toFixed(1)}</p>
                  <p className="text-xs text-green-600">out of 10</p>
                </div>
                <TrendingUp className="w-12 h-12 text-green-400 opacity-60" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-yellow-700 mb-1">Top Score</p>
                  <p className="text-3xl font-bold text-yellow-900">{stats.highest_score}</p>
                  <p className="text-xs text-yellow-600">⭐ Excellence</p>
                </div>
                <Trophy className="w-12 h-12 text-yellow-500 opacity-60" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-emerald-700 mb-1">Excellent</p>
                  <p className="text-3xl font-bold text-emerald-900">{stats.excellent}</p>
                  <p className="text-xs text-emerald-600">9.0+ score</p>
                </div>
                <CheckCircle className="w-12 h-12 text-emerald-400 opacity-60" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-sky-50 to-sky-100 border-sky-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-sky-700 mb-1">Good</p>
                  <p className="text-3xl font-bold text-sky-900">{stats.good}</p>
                  <p className="text-xs text-sky-600">8.0-8.9</p>
                </div>
                <CheckCircle className="w-12 h-12 text-sky-400 opacity-60" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase font-semibold text-orange-700 mb-1">Needs Focus</p>
                  <p className="text-3xl font-bold text-orange-900">{stats.needs_improvement + stats.poor}</p>
                  <p className="text-xs text-orange-600">Below 7.0</p>
                </div>
                <AlertCircle className="w-12 h-12 text-orange-400 opacity-60" />
              </div>
            </Card>
          </div>
        )}

        {/* Main Performance Table */}
        <Card className="overflow-hidden shadow-lg">
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
            <h2 className="text-xl font-bold text-gray-800">Engineer Performance Ranking</h2>
            <p className="text-sm text-gray-600 mt-1">Sorted by driving score - Top performers first</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100 border-b-2 border-gray-300">
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Engineer Name</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Van</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">Performance</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">Score</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                        <p className="text-gray-600 font-medium">Loading performance data...</p>
                      </div>
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center">
                      <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                      <p className="text-red-600 font-semibold">{error}</p>
                    </td>
                  </tr>
                ) : engineers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      No engineers found
                    </td>
                  </tr>
                ) : (
                  engineers.map((engineer) => (
                    <tr 
                      key={engineer.rank} 
                      className={`border-b transition-all duration-200 ${getRowColor(engineer.score_class)}`}
                    >
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2">
                          {getRankBadge(engineer.rank)}
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <p className="font-semibold text-gray-900 text-lg">{engineer.name}</p>
                        {engineer.rank <= 3 && (
                          <p className="text-xs text-gray-500 mt-1">⭐ Top Performer</p>
                        )}
                      </td>
                      <td className="px-6 py-5">
                        <Badge variant="outline" className="font-mono font-semibold">
                          {engineer.van_number}
                        </Badge>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex justify-center">
                          <Badge className={`${getScoreBadgeColor(engineer.score_class)} px-4 py-1 font-semibold border`}>
                            {engineer.score_class.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex items-center justify-center gap-3">
                          {getScoreIcon(engineer.score)}
                          <div className="text-center">
                            <p className="font-bold text-2xl text-gray-900">{engineer.score.toFixed(1)}</p>
                            <p className="text-xs text-gray-500 font-medium">/ 10</p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Score Legend */}
        <Card className="p-6 bg-gradient-to-r from-gray-50 to-gray-100">
          <h3 className="font-bold text-lg mb-4 text-gray-800">📊 Performance Score Scale</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="p-4 bg-green-100 border-2 border-green-400 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Trophy className="w-5 h-5 text-green-700" />
                <p className="font-bold text-green-900">Excellent</p>
              </div>
              <p className="text-2xl font-bold text-green-800">9.0 - 10.0</p>
              <p className="text-xs text-green-700 mt-1">Outstanding performance</p>
            </div>
            
            <div className="p-4 bg-blue-100 border-2 border-blue-400 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-blue-700" />
                <p className="font-bold text-blue-900">Good</p>
              </div>
              <p className="text-2xl font-bold text-blue-800">8.0 - 8.9</p>
              <p className="text-xs text-blue-700 mt-1">Above average</p>
            </div>
            
            <div className="p-4 bg-yellow-100 border-2 border-yellow-400 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-yellow-700" />
                <p className="font-bold text-yellow-900">Fair</p>
              </div>
              <p className="text-2xl font-bold text-yellow-800">7.0 - 7.9</p>
              <p className="text-xs text-yellow-700 mt-1">Satisfactory</p>
            </div>
            
            <div className="p-4 bg-orange-100 border-2 border-orange-400 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5 text-orange-700" />
                <p className="font-bold text-orange-900">Needs Improvement</p>
              </div>
              <p className="text-2xl font-bold text-orange-800">6.0 - 6.9</p>
              <p className="text-xs text-orange-700 mt-1">Requires attention</p>
            </div>
            
            <div className="p-4 bg-red-100 border-2 border-red-400 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5 text-red-700" />
                <p className="font-bold text-red-900">Poor</p>
              </div>
              <p className="text-2xl font-bold text-red-800">Below 6.0</p>
              <p className="text-xs text-red-700 mt-1">Immediate action needed</p>
            </div>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Webfleet;