"use client"
import { useEffect, useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

const REQUIRED_COLS = [
  "Date", "SKU_ID", "Warehouse_ID", "Supplier_ID", "Region", 
  "Units_Sold", "Inventory_Level", "Supplier_Lead_Time_Days", 
  "Reorder_Point", "Order_Quantity", "Unit_Cost", "Unit_Price", 
  "Promotion_Flag", "Stockout_Flag", "Demand_Forecast"
];

export default function SchemaValidator({ file, onValid }) {
  const [cols, setCols] = useState([]);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const header = text.split('\n')[0];
      const uploadedCols = header.split(',').map(c => c.trim().replace(/^"|"$/g, ''));
      setCols(uploadedCols);
      
      const valid = REQUIRED_COLS.every(c => uploadedCols.includes(c));
      setIsValid(valid);
      if (valid) onValid();
    };
    reader.readAsText(file.slice(0, 1024)); // Read header
  }, [file, onValid]);

  return (
    <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.08)] p-6 rounded-xl">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        {isValid ? <CheckCircle className="text-green-500" /> : <XCircle className="text-red-500" />}
        Schema Validation {isValid ? "Passed" : "Failed"}
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {REQUIRED_COLS.map(c => {
          const present = cols.includes(c);
          return (
            <div key={c} className={`flex items-center gap-2 text-sm ${present ? 'text-gray-300' : 'text-red-400'}`}>
              {present ? <CheckCircle size={16} className="text-green-500"/> : <XCircle size={16}/>}
              {c}
            </div>
          )
        })}
      </div>
    </div>
  )
}
