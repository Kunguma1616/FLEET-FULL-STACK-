import { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Upload as UploadIcon,
  Loader2,
  Search,
  ArrowLeft,
  AlertCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface VehicleData {
  van_number: string;
  registration_number: string;
  tracking_number: string;
  vehicle_name: string;
  driver_history: string;
  vehicle_type: string;
  description: string;
  ai_details: string;
}

interface AvailableVehicle {
  van_number: string;
  name: string;
  registration_number: string;
  vehicle_type: string;
}

export default function Upload() {
  const navigate = useNavigate();
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [vanNumber, setVanNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [vehicleData, setVehicleData] = useState<VehicleData | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestedVehicles, setSuggestedVehicles] = useState<AvailableVehicle[]>([]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setPreviewUrl(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleSearchVehicle = async () => {
    if (!vanNumber.trim()) {
      toast.error('Please enter a van number');
      return;
    }

    setLoading(true);
    try {
      const url = `/api/vehicles/lookup/${vanNumber.trim()}`;
      console.log('Fetching from:', url);
      
      const response = await fetch(url);
      
      // Check content type to diagnose HTML responses
      const contentType = response.headers.get('content-type');
      console.log('Response content-type:', contentType);
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        // Try to get error details
        const text = await response.text();
        console.error('Response body:', text);
        throw new Error(`Vehicle not found (${response.status}). Please check the van number.`);
      }

      const data = await response.json();
      
      // Extract AI details from image if available
      let aiDetails = data.ai_details || '';
      if (imageFile) {
        aiDetails = await extractImageDetails();
      }

      setVehicleData({
        van_number: data.van_number || vanNumber,
        registration_number: data.registration_number || 'N/A',
        tracking_number: data.tracking_number || 'N/A',
        vehicle_name: data.vehicle_name || 'N/A',
        driver_history: data.driver_history || 'No driver history available',
        vehicle_type: data.vehicle_type || 'N/A',
        description: data.description || 'N/A',
        ai_details: aiDetails
      });

      toast.success('Vehicle information loaded successfully!');
    } catch (error) {
      console.error('Search error:', error);
      
      // If van not found, try to fetch available vehicles
      if (error instanceof Error && error.message.includes('404')) {
        try {
          const response = await fetch('/api/vehicles/search');
          const data = await response.json();
          setSuggestedVehicles(data.vehicles || []);
          setShowSuggestions(true);
          toast.error(`Van number '${vanNumber}' not found. See suggestions below.`);
        } catch (e) {
          toast.error(error instanceof Error ? error.message : 'Failed to fetch vehicle data. Is the backend running on port 8000?');
        }
      } else {
        toast.error(error instanceof Error ? error.message : 'Failed to fetch vehicle data. Is the backend running on port 8000?');
      }
    } finally {
      setLoading(false);
    }
  };

  const extractImageDetails = async (): Promise<string> => {
    if (!imageFile) return '';

    try {
      // Call AI service to extract details from image
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('van_number', vanNumber);

      const response = await fetch('/api/ai/extract-vehicle-details', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        console.warn('AI extraction failed, continuing without image analysis');
        return '';
      }

      const data = await response.json();
      return data.details || '';
    } catch (error) {
      console.warn('AI extraction error:', error);
      return '';
    }
  };

  const handleSaveAsset = async () => {
    if (!vehicleData) {
      toast.error('No vehicle data to save');
      return;
    }

    setUploading(true);
    try {
      const payload = {
        ...vehicleData,
        image_data: previewUrl // Store base64 image
      };

      const response = await fetch('/api/assets/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Failed to save asset');
      }

      toast.success('Asset saved successfully! Redirecting to Assets page...');
      setTimeout(() => {
        navigate('/assets');
      }, 1500);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to save asset');
    } finally {
      setUploading(false);
    }
  };

  const handleClear = () => {
    setImageFile(null);
    setPreviewUrl('');
    setVanNumber('');
    setVehicleData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft size={20} />
            Back
          </button>
          <h1 className="text-4xl font-bold text-gray-800">Upload Vehicle</h1>
          <p className="text-gray-600 mt-2">Upload an image and enter the van number to fetch vehicle details</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Image Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UploadIcon size={20} />
                Vehicle Image
              </CardTitle>
              <CardDescription>Upload a photo of the vehicle</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageSelect}
                    className="hidden"
                  />

                  <div
                    onClick={openFilePicker}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragEnter={handleDragOver}
                    onDragLeave={handleDragLeave}
                    role="button"
                    tabIndex={0}
                    className={`w-full h-64 rounded-lg border-2 flex items-center justify-center cursor-pointer transition p-4 ${
                      dragActive ? 'border-blue-400 bg-blue-50' : 'border-dashed border-gray-300 bg-white'
                    }`}
                  >
                    {previewUrl ? (
                      <div className="relative w-full h-full">
                        <img
                          src={previewUrl}
                          alt="Vehicle preview"
                          className="w-full h-full object-cover rounded-lg"
                        />
                        <div className="absolute top-2 right-2 flex gap-2">
                          <button
                            onClick={(ev) => {
                              ev.stopPropagation();
                              setPreviewUrl('');
                              setImageFile(null);
                            }}
                            className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500">
                        <UploadIcon size={36} className="mx-auto mb-3" />
                        <p className="font-semibold">Drag & drop an image here</p>
                        <p className="text-sm mt-1">or click to browse files</p>
                        <p className="text-xs text-gray-400 mt-2">PNG, JPG, GIF — max 10MB</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Right Column - Vehicle Lookup */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search size={20} />
                Vehicle Information
              </CardTitle>
              <CardDescription>Search by van number</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="van-number">Van Number *</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      id="van-number"
                      placeholder="e.g., VEH-00001"
                      value={vanNumber}
                      onChange={(e) => setVanNumber(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearchVehicle()}
                      disabled={loading}
                    />
                    <Button
                      onClick={handleSearchVehicle}
                      disabled={loading || !vanNumber.trim()}
                      className="whitespace-nowrap"
                    >
                      {loading ? <Loader2 size={16} className="animate-spin" /> : 'Search'}
                    </Button>
                  </div>
                </div>

                {showSuggestions && suggestedVehicles.length > 0 && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <p className="text-sm font-semibold text-amber-900 mb-2">Did you mean one of these?</p>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {suggestedVehicles.slice(0, 10).map((vehicle) => (
                        <button
                          key={vehicle.van_number}
                          onClick={() => {
                            setVanNumber(vehicle.van_number);
                            setShowSuggestions(false);
                            setTimeout(() => handleSearchVehicle(), 100);
                          }}
                          className="w-full text-left p-2 hover:bg-amber-100 rounded border border-amber-100 text-sm transition"
                        >
                          <span className="font-semibold text-amber-900">{vehicle.van_number}</span>
                          {' - '}
                          <span className="text-amber-800">{vehicle.registration_number}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {vehicleData && (
                  <div className="space-y-3 pt-4 border-t">
                    <div>
                      <Label className="text-xs text-gray-500">Registration Number</Label>
                      <p className="text-lg font-semibold text-gray-800">{vehicleData.registration_number}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-gray-500">Tracking Number</Label>
                      <p className="text-lg font-semibold text-gray-800">{vehicleData.tracking_number}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-gray-500">Vehicle Type</Label>
                      <p className="text-sm text-gray-700">{vehicleData.vehicle_type}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-gray-500">Vehicle Name</Label>
                      <p className="text-sm text-gray-700">{vehicleData.vehicle_name}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Driver History Section */}
        {vehicleData && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Complete Driver History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-gray-700 whitespace-pre-wrap">{vehicleData.driver_history}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Description Section */}
        {vehicleData && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Vehicle Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{vehicleData.description}</p>
            </CardContent>
          </Card>
        )}

        {/* AI Details Section */}
        {vehicleData && vehicleData.ai_details && (
          <Card className="mt-6 border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="text-blue-900">AI Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-white p-4 rounded-lg border border-blue-200">
                <p className="text-gray-700 whitespace-pre-wrap">{vehicleData.ai_details}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        {vehicleData && (
          <div className="flex gap-3 mt-8 justify-end">
            <Button
              variant="outline"
              onClick={handleClear}
              disabled={uploading}
            >
              Clear
            </Button>
            <Button
              onClick={handleSaveAsset}
              disabled={uploading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {uploading ? (
                <>
                  <Loader2 size={16} className="animate-spin mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <UploadIcon size={16} className="mr-2" />
                  Save as Asset
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
