import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Upload as UploadIcon,
  Loader2,
  ArrowLeft,
  Search,
  Eye,
  Calendar
} from 'lucide-react';

interface Asset {
  id: string;
  name: string;
  van_number: string;
  registration_number: string;
  tracking_number: string;
  vehicle_type: string;
  description: string;
  status: string;
  created_date: string;
}

export default function AssetsGallery() {
  const navigate = useNavigate();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedAsset, setExpandedAsset] = useState<string | null>(null);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/assets/all');
      
      if (!response.ok) {
        throw new Error('Failed to fetch assets');
      }

      const data = await response.json();
      setAssets(data.assets || []);
      setFilteredAssets(data.assets || []);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to load assets');
      setAssets([]);
      setFilteredAssets([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    const filtered = assets.filter((asset) =>
      asset.van_number?.includes(term) ||
      asset.registration_number?.includes(term) ||
      asset.name?.toLowerCase().includes(term.toLowerCase()) ||
      asset.tracking_number?.includes(term)
    );
    setFilteredAssets(filtered);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    const statusStyles: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
      'Uploaded': { variant: 'default' },
      'Allocated': { variant: 'secondary' },
      'Spare': { variant: 'outline' },
      'Written Off': { variant: 'destructive' },
      'Reserved': { variant: 'secondary' }
    };

    return statusStyles[status] || { variant: 'outline' };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft size={20} />
            Back
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-gray-800">Vehicle Assets</h1>
              <p className="text-gray-600 mt-2">View all uploaded vehicle details with images and AI analysis</p>
            </div>
            <Button
              onClick={() => navigate('/upload')}
              className="bg-blue-600 hover:bg-blue-700 gap-2"
            >
              <UploadIcon size={20} />
              Upload New Vehicle
            </Button>
          </div>
        </div>

        {/* Search Bar */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex gap-3">
              <Search className="text-gray-400 flex-shrink-0 mt-2" size={20} />
              <Input
                placeholder="Search by van number, registration, tracking number, or vehicle name..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="flex-1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <Loader2 size={40} className="animate-spin text-blue-600" />
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredAssets.length === 0 && (
          <Card className="text-center py-16">
            <CardContent>
              <UploadIcon size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Assets Found</h3>
              <p className="text-gray-600 mb-6">
                {assets.length === 0
                  ? "Start by uploading your first vehicle"
                  : "Try adjusting your search criteria"}
              </p>
              {assets.length === 0 && (
                <Button
                  onClick={() => navigate('/upload')}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Upload First Vehicle
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {/* Assets Grid */}
        {!loading && filteredAssets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAssets.map((asset) => (
              <Card
                key={asset.id}
                className="hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
                onClick={() => setExpandedAsset(expandedAsset === asset.id ? null : asset.id)}
              >
                {/* Placeholder Vehicle Image */}
                <div className="bg-gradient-to-br from-blue-200 to-indigo-200 h-48 flex items-center justify-center">
                  <div className="text-center">
                    <UploadIcon size={48} className="mx-auto text-blue-600 mb-2 opacity-50" />
                    <p className="text-blue-700 font-semibold">Van {asset.van_number}</p>
                  </div>
                </div>

                <CardHeader>
                  <div className="flex justify-between items-start gap-2 mb-2">
                    <CardTitle className="text-lg">{asset.name}</CardTitle>
                    <Badge variant={getStatusBadge(asset.status).variant}>
                      {asset.status}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Key Information */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Van #:</span>
                      <span className="font-semibold text-gray-900">{asset.van_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Registration:</span>
                      <span className="font-semibold text-gray-900">{asset.registration_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tracking #:</span>
                      <span className="font-semibold text-gray-900">{asset.tracking_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-semibold text-gray-900">{asset.vehicle_type}</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Calendar size={14} />
                      {formatDate(asset.created_date)}
                    </p>
                  </div>

                  {/* Description (collapsible) */}
                  {expandedAsset === asset.id && (
                    <div className="mt-4 pt-4 border-t bg-gray-50 p-3 rounded">
                      <p className="text-sm text-gray-700">
                        <strong>Description:</strong> {asset.description}
                      </p>
                    </div>
                  )}

                  {/* View Details Button */}
                  <Button
                    variant="outline"
                    className="w-full mt-4 gap-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/assets/${asset.id}`, { state: { asset } });
                    }}
                  >
                    <Eye size={16} />
                    View Full Details
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Summary */}
        {!loading && assets.length > 0 && (
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-center text-blue-900">
              Showing <strong>{filteredAssets.length}</strong> of <strong>{assets.length}</strong> uploaded vehicles
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
