"use client"
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function JobProgressBar({ jobId }) {
  const [job, setJob] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const interval = setInterval(async () => {
      const data = await api.pipeline.getJob(jobId);
      setJob(data);
      if (data.status === 'done') {
        clearInterval(interval);
        setTimeout(() => router.push(`/results/${jobId}`), 1000);
      }
      if (data.status === 'failed') {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId, router]);

  if (!job) return <div className="text-center text-gray-400">Initializing Tracking...</div>;

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.08)] p-8 rounded-xl text-center space-y-6">
        <h3 className="text-xl font-bold">{job.current_step}</h3>
        
        <div className="h-4 bg-gray-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 transition-all duration-500"
            style={{ width: `${job.progress}%` }}
          />
        </div>
        
        <p className="text-sm font-mono text-gray-400">{job.progress}% Complete</p>
        
        {job.status === 'failed' && <p className="text-red-500">{job.error}</p>}
      </div>
    </div>
  )
}
