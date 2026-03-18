"use client"
import { useState, useCallback, useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import SchemaValidator from './SchemaValidator';
import { api } from '@/lib/api';

export default function DropZone({ onUploadStart, onJobStarted }) {
  const [file, setFile] = useState(null);
  const [schemaValid, setSchemaValid] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile);
      setSchemaValid(false); 
    }
  };
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setSchemaValid(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !schemaValid) return;
    setUploading(true);
    onUploadStart();
    try {
        const res = await api.pipeline.upload(file);
        onJobStarted(res.job_id);
    } catch(e) {
        console.error(e);
        setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div 
        onDrop={handleDrop} 
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className={`cursor-pointer border-2 border-dashed rounded-xl p-12 text-center transition-colors ${file ? 'border-blue-500 bg-blue-500/5' : 'border-gray-600 hover:border-gray-500 bg-[rgba(255,255,255,0.02)]'}`}
      >
        <UploadCloud size={48} className="mx-auto mb-4 text-gray-400" />
        {file ? (
          <div className="text-white font-medium">{file.name}</div>
        ) : (
          <div>
            <p className="text-lg font-medium text-white mb-2">Drag and drop your CSV here</p>
            <p className="text-sm text-gray-400">or click to browse</p>
          </div>
        )}
      </div>
      
      <input type="file" accept=".csv" className="hidden" ref={fileInputRef} onChange={handleFileChange} />

      {file && <SchemaValidator file={file} onValid={() => setSchemaValid(true)} />}

      <button 
        onClick={handleUpload}
        disabled={!file || !schemaValid || uploading}
        className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-400 rounded-xl font-bold text-lg transition-colors"
      >
        {uploading ? "Uploading..." : "Start Pipeline"}
      </button>
    </div>
  )
}
