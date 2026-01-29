import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
// Layout provided by App's ProtectedRoute
import { KpiCard } from '@/components/dashboard/KpiCard';
import { TradeGroupStackedChart } from '@/components/dashboard/TradeGroupStackedChart';
import { VehicleTypeStackedChart } from '@/components/dashboard/VehicleTypeStackedChart';
import { SpareVehiclesChart } from '@/components/dashboard/SpareVehiclesChart';
import { LeaversVehiclesChart } from '@/components/dashboard/LeaversVehiclesChart';
import { VehicleDataSheet } from '@/components/dashboard/VehicleDataSheet';
import { Button } from '@/components/ui/button';
import { API_ENDPOINTS } from '@/config/api';
import { 
  Car, 
  CheckCircle, 
  Wrench, 
  AlertTriangle, 
  Calendar, 
  Settings,
  Zap,
  Upload as UploadIcon,
  Image as ImageIcon,
} from 'lucide-react';
import {
  tradeGroupChartData,
  vehicleTypeChartData,
  spareVansByTradeGroup,
  leaversByVanNumber,
  VehicleRecord,
} from '@/data/fleetData';

interface VehicleSummary {
  total: number;
  allocated: number;
  garage: number;
  due_service: number;
  spare_ready: number;
  reserved: number;
  written_off: number;
  mot_due: number;
  tax_due: number;
}

interface SalesforceVehicle {
  Id: string;
  Name: string;
  Reg_No__c?: string;
  Van_Number__c?: string;
  Status__c?: string;
  Trade_Group__c?: string;
  Vehicle_Type__c?: string;
  Make_Model__c?: string;
}

interface VehiclesByStatusResponse {
  status: string;
  count: number;
  vehicles: SalesforceVehicle[];
}

type SheetType = 'current' | 'allocated' | 'garage' | 'writtenOff' | 'mot' | 'service' | null;

const FleetDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeSheet, setActiveSheet] = useState<SheetType>(null);
  const [summary, setSummary] = useState<VehicleSummary | null>(null);
  const [sheetVehicles, setSheetVehicles] = useState<VehicleRecord[]>([]);
  const [sheetData, setSheetData] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVehicleSummary();
  }, []);

  const fetchVehicleSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(API_ENDPOINTS.VEHICLE_SUMMARY);
      console.log('Vehicle summary response:', response.data);
      setSummary(response.data);
    } catch (err) {
      console.error('Failed to fetch vehicle summary:', err);
      setError('Failed to load dashboard data from Salesforce');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllVehicles = async (title: string, description: string) => {
    try {
      const response = await axios.get<VehiclesByStatusResponse>(
        API_ENDPOINTS.VEHICLES_BY_STATUS('total')
      );

      const convertedVehicles: VehicleRecord[] = response.data.vehicles.map((v: any) => ({
        id: v.Id,
        name: v.Name || '',
        vanNumber: v.Van_Number__c || v.Name || '',
        regNo: v.Reg_No__c || '',
        status: v.Status__c || '',
        vehicleType: v.Vehicle_Type__c || v.Make_Model__c || '',
        tradeGroup: v.Trade_Group__c || '',
        serviceCost: v.service_cost != null ? v.service_cost : (v.Next_Service_Date__c || ''),
        maintenanceCost: v.maintenance_cost != null ? v.maintenance_cost : (v.Next_MOT_Date__c || ''),
      } as unknown as VehicleRecord));

      setSheetVehicles(convertedVehicles);
      setSheetData({ title, description });
      setActiveSheet('current');
    } catch (err) {
      console.error('Failed to fetch all vehicles:', err);
      alert('Failed to load vehicle data');
    }
  };

  const fetchVehiclesByStatus = async (status: string, title: string, description: string) => {
    try {
      const statusMap: Record<string, string> = {
        'allocated': 'allocated',
        'garage': 'garage',
        'writtenOff': 'written_off',
        'mot': 'due_service',
        'service': 'due_service',
      };

      const apiStatus = statusMap[status] || status;
      const response = await axios.get<VehiclesByStatusResponse>(
        API_ENDPOINTS.VEHICLES_BY_STATUS(apiStatus)
      );

      // Convert Salesforce vehicle format to VehicleRecord format
      const convertedVehicles: VehicleRecord[] = response.data.vehicles.map((v: any) => ({
        id: v.Id,
        name: v.Name || '',
        // VehicleDataSheet expects these property names:
        vanNumber: v.Van_Number__c || v.Name || '',
        regNo: v.Reg_No__c || '',
        status: v.Status__c || '',
        vehicleType: v.Vehicle_Type__c || v.Make_Model__c || '',
        tradeGroup: v.Trade_Group__c || '',
        // use aggregated cost values if available, otherwise fall back to next service/MOT date
        serviceCost: v.service_cost != null ? v.service_cost : (v.Next_Service_Date__c || ''),
        maintenanceCost: v.maintenance_cost != null ? v.maintenance_cost : (v.Next_MOT_Date__c || ''),
      } as unknown as VehicleRecord));

      setSheetVehicles(convertedVehicles);
      setSheetData({ title, description });
      setActiveSheet(status as SheetType);
    } catch (err) {
      console.error(`Failed to fetch ${status} vehicles:`, err);
      alert(`Failed to load ${title} data`);
    }
  };

  const fetchMotDue = async (title: string, description: string) => {
    try {
      const response = await axios.get(API_ENDPOINTS.VEHICLES_MOT_DUE);
      const convertedVehicles: VehicleRecord[] = response.data.vehicles.map((v: any) => ({
        id: v.Id,
        name: v.Name || '',
        vanNumber: v.Van_Number__c || v.Name || '',
        regNo: v.Reg_No__c || '',
        status: v.Status__c || '',
        vehicleType: v.Vehicle_Type__c || v.Make_Model__c || '',
        tradeGroup: v.Trade_Group__c || '',
        serviceCost: v.service_cost != null ? v.service_cost : (v.Next_Service_Date__c || ''),
        maintenanceCost: v.maintenance_cost != null ? v.maintenance_cost : (v.Next_MOT_Date__c || ''),
      } as unknown as VehicleRecord));

      setSheetVehicles(convertedVehicles);
      setSheetData({ title, description });
      setActiveSheet('mot');
    } catch (err) {
      console.error('Failed to fetch MOT due vehicles:', err);
      alert('Failed to load MOT due vehicles');
    }
  };

  const fetchServiceDue = async (title: string, description: string) => {
    try {
      const response = await axios.get(API_ENDPOINTS.VEHICLES_SERVICE_DUE);
      const convertedVehicles: VehicleRecord[] = response.data.vehicles.map((v: any) => ({
        id: v.Id,
        name: v.Name || '',
        vanNumber: v.Van_Number__c || v.Name || '',
        regNo: v.Reg_No__c || '',
        status: v.Status__c || '',
        vehicleType: v.Vehicle_Type__c || v.Make_Model__c || '',
        tradeGroup: v.Trade_Group__c || '',
        serviceCost: v.service_cost != null ? v.service_cost : (v.Next_Service_Date__c || ''),
        maintenanceCost: v.maintenance_cost != null ? v.maintenance_cost : (v.Next_MOT_Date__c || ''),
      } as unknown as VehicleRecord));

      setSheetVehicles(convertedVehicles);
      setSheetData({ title, description });
      setActiveSheet('service');
    } catch (err) {
      console.error('Failed to fetch service due vehicles:', err);
      alert('Failed to load service due vehicles');
    }
  };

  const fetchTaxDue = async (title: string, description: string) => {
    try {
      const response = await axios.get(API_ENDPOINTS.VEHICLES_TAX_DUE);
      const convertedVehicles: VehicleRecord[] = response.data.vehicles.map((v: any) => ({
        id: v.Id,
        name: v.Name || '',
        vanNumber: v.Van_Number__c || v.Name || '',
        regNo: v.Reg_No__c || '',
        status: v.Status__c || '',
        vehicleType: v.Vehicle_Type__c || v.Make_Model__c || '',
        tradeGroup: v.Trade_Group__c || '',
        serviceCost: v.service_cost != null ? v.service_cost : (v.Next_Service_Date__c || ''),
        maintenanceCost: v.maintenance_cost != null ? v.maintenance_cost : (v.Next_MOT_Date__c || ''),
      } as unknown as VehicleRecord));

      setSheetVehicles(convertedVehicles);
      setSheetData({ title, description });
      setActiveSheet('service');
    } catch (err) {
      console.error('Failed to fetch road tax due vehicles:', err);
      alert('Failed to load road tax due vehicles');
    }
  };

  return (
    <>
      <div className="space-y-6">
        {/* Top Navigation Buttons */}
        <div className="flex justify-end gap-3">
          <Button 
            onClick={() => navigate('/assets')}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700"
          >
            <ImageIcon className="w-4 h-4" />
            Asset Portfolio
          </Button>
          <Button 
            onClick={() => navigate('/upload')}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
          >
            <UploadIcon className="w-4 h-4" />
            Upload Vehicle
          </Button>
          <Button 
            onClick={() => navigate('/webfleet')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
          >
            <Zap className="w-4 h-4" />
            View Driving Performance
          </Button>
        </div>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <KpiCard
            title="Current Vehicles"
            value={summary?.total ?? 0}
            variant="positive"
            icon={Car}
            subtitle="Active fleet size"
            onClick={() => fetchAllVehicles('All Vehicles', 'All active vehicles in the fleet')}
          />
          <KpiCard
            title="Allocated Vehicles"
            value={summary?.allocated ?? 0}
            variant="positive"
            icon={CheckCircle}
            subtitle="Assigned to drivers"
            onClick={() => fetchVehiclesByStatus('allocated', 'Allocated Vehicles', 'Vehicles assigned to drivers')}
          />
          <KpiCard
            title="Vehicles in Garage"
            value={summary?.garage ?? 0}
            variant="negative"
            icon={Wrench}
            subtitle="Under repair"
            onClick={() => fetchVehiclesByStatus('garage', 'Vehicles in Garage', 'Vehicles currently under repair')}
          />
          <KpiCard
            title="Written Off Vehicles"
            value={summary?.written_off ?? 0}
            variant="negative"
            icon={AlertTriangle}
            subtitle="Decommissioned"
            onClick={() => fetchVehiclesByStatus('writtenOff', 'Written Off Vehicles', 'Decommissioned vehicles')}
          />
          <KpiCard
            title="Due for Service"
            value={summary?.due_service ?? 0}
            variant="negative"
            icon={Calendar}
            subtitle="Requires attention"
            onClick={() => fetchServiceDue('Vehicles to Service', 'Vehicles scheduled for service')}
          />
          <KpiCard
            title="Spare Vehicles"
            value={summary?.spare_ready ?? 0}
            variant="positive"
            icon={Settings}
            subtitle="Ready to deploy"
            onClick={() => fetchVehiclesByStatus('spare_ready', 'Spare Vehicles', 'Vehicles ready for deployment')}
          />
        </div>

        {/* Additional Row: MOT Due & Road Tax Due */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <KpiCard
            title="MOT Due in 30 Days"
            value={summary?.mot_due ?? 0}
            variant="negative"
            icon={Calendar}
            subtitle="Requires attention"
            onClick={() => fetchMotDue('MOT Due in 30 Days', 'Vehicles with MOT expiring soon')}
          />
          <KpiCard
            title="Road Tax Due"
            value={summary?.tax_due ?? 0}
            variant="negative"
            icon={AlertTriangle}
            subtitle="Tax renewal needed"
            onClick={() => fetchTaxDue('Road Tax Due', 'Vehicles with road tax expiring soon')}
          />
        </div>

        {/* Charts Section - Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TradeGroupStackedChart
            data={tradeGroupChartData}
            title="All Vehicles by Trade Group"
          />
          <VehicleTypeStackedChart
            data={vehicleTypeChartData}
            title="All Vehicles by Vehicle Type"
          />
        </div>

        {/* Charts Section - Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SpareVehiclesChart
            data={spareVansByTradeGroup}
            title="Spare Vehicles Ready"
          />
          <LeaversVehiclesChart
            data={leaversByVanNumber}
            title="Leavers Vehicles"
          />
        </div>
      </div>

      {/* Vehicle Data Sheet */}
      <VehicleDataSheet
        open={activeSheet !== null}
        onOpenChange={(open) => !open && setActiveSheet(null)}
        title={sheetData.title}
        description={sheetData.description}
        vehicles={sheetVehicles}
      />
    </>
  );
};

export default FleetDashboard;
