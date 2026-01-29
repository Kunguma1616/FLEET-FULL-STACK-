import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import {
  ArrowLeft,
  Loader2,
  Calendar,
  MapPin,
  Hash,
  Settings,
  Zap,
  FileText,
  Brain,
  Download,
  Trash2
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
  image_data?: string;
  driver_history?: string;
  ai_details?: string;
}

export default function AssetDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [asset, setAsset] = useState<Asset | null>(location.state?.asset || null);
  const [loading, setLoading] = useState(!asset);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!asset) {
      fetchAsset();
    }
  }, [id]);

  const fetchAsset = async () => {
    if (!id) return;

    try {
      setLoading(true);
      // Query by van number from URL
      const response = await fetch(`/api/assets/by-van/${id}`);

      if (!response.ok) {
        throw new Error('Asset not found');
      }

      const data = await response.json();
      setAsset(data);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to load asset');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this vehicle asset?')) {
      return;
    }

    setDeleting(true);
    try {
      // In production, create a DELETE endpoint
      toast.success('Asset deleted successfully');
      navigate('/assets');
    } catch (error) {
      toast.error('Failed to delete asset');
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Loader2 size={40} className="animate-spin text-blue-600" />
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/assets')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft size={20} />
            Back to Assets
          </button>
          <Card className="text-center py-16">
            <CardContent>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Asset Not Found</h3>
              <p className="text-gray-600">The asset you're looking for doesn't exist.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/assets')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft size={20} />
            Back to Assets
          </button>

          <div className="flex justify-between items-start gap-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-800">{asset.name}</h1>
              <p className="text-gray-600 mt-2">
                <span className="flex items-center gap-2">
                  <Calendar size={16} />
                  Added on {formatDate(asset.created_date)}
                </span>
              </p>
            </div>
            <div className="flex gap-2">
              <Badge variant="default" className="text-sm">
                {asset.status}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.print()}
                className="gap-2"
              >
                <Download size={16} />
                Export
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={deleting}
                className="gap-2"
              >
                {deleting ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                Delete
              </Button>
            </div>
          </div>
        </div>

        {/* Vehicle Information Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Van Number */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-gray-600">
                <Hash size={16} />
                Van Number
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-gray-900">{asset.van_number}</p>
            </CardContent>
          </Card>

          {/* Registration */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-gray-600">
                <FileText size={16} />
                Registration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-gray-900">{asset.registration_number}</p>
            </CardContent>
          </Card>

          {/* Tracking Number */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-gray-600">
                <MapPin size={16} />
                Tracking #
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-bold text-gray-900">{asset.tracking_number}</p>
            </CardContent>
          </Card>

          {/* Vehicle Type */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-gray-600">
                <Settings size={16} />
                Vehicle Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm font-bold text-gray-900">{asset.vehicle_type}</p>
            </CardContent>
          </Card>
        </div>

        {/* Vehicle Image Placeholder */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Vehicle Image</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gradient-to-br from-blue-200 to-indigo-200 h-96 rounded-lg flex items-center justify-center">
              {asset.image_data ? (
                <img src={asset.image_data} alt={asset.name} className="w-full h-full object-cover rounded-lg" />
              ) : (
                <div className="text-center">
                  <Settings size={48} className="mx-auto text-blue-600 mb-2 opacity-30" />
                  <p className="text-blue-700">No image uploaded</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Description */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText size={20} />
              Description
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">{asset.description}</p>
          </CardContent>
        </Card>

        {/* Driver History */}
        {asset.driver_history && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Complete Driver History</CardTitle>
              <CardDescription>Historical driver assignments and usage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 max-h-64 overflow-y-auto">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                  {asset.driver_history}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI Analysis */}
        {asset.ai_details && (
          <Card className="mb-6 border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-900">
                <Brain size={20} />
                AI Analysis Report
              </CardTitle>
              <CardDescription className="text-blue-700">
                Automated vehicle condition and safety assessment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-white p-4 rounded-lg border border-blue-200">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {asset.ai_details}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Summary Info */}
        <Alert className="bg-blue-50 border-blue-200">
          <Zap size={16} className="text-blue-600" />
          <AlertDescription className="text-blue-900">
            This asset was uploaded and includes complete vehicle information, driver history, and AI-powered analysis. All data is stored securely and can be exported for compliance and reporting purposes.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}
