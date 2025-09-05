import React, { useState, useRef } from 'react';
import axios from 'axios';


function S3Uploader() {
  const [file, setFile] = useState(null);
  const [s3Link, setS3Link] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setS3Link('');
    setError('');
    setProgress(0);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    setUploading(true);
    setError('');
    setS3Link('');
    setProgress(0);

    const formData = new FormData();
    formData.append('bucket', 'Add bucket name here');
    formData.append('directory', 'Add directory path here');
    formData.append('file', file);

    try {
      const response = await axios.post(
        'Add S3 Attachment URL here',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setProgress(percent);
            }
          },
        }
      );
      const data = response.data;
      if (data.Status && data.lstAttachments && data.lstAttachments.length > 0) {
        setS3Link(data.lstAttachments[0].imgPath);
      } else {
        setError(data.Message || data.ErrorMessage || 'Upload failed');
      }
    } catch (err) {
      setError('Upload error: ' + (err.response?.data?.Message || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{
      maxWidth: 360,
      margin: '40px auto',
      padding: '32px 24px',
      background: '#fff',
      borderRadius: '16px',
      boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      fontFamily: 'Inter, Arial, sans-serif'
    }}>
      <h2 style={{ fontWeight: 600, fontSize: 22, marginBottom: 18, color: '#222' }}>S3 File Uploader</h2>
      <div style={{ width: '100%', marginBottom: 18 }}>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current.click()}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: '8px',
            border: '2px dashed #4caf50',
            background: file ? '#e8f5e9' : '#fafafa',
            color: '#333',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'background 0.2s',
            marginBottom: 6
          }}
        >
          {file ? `Selected: ${file.name}` : 'Select a file'}
        </button>
      </div>
      <button
        onClick={handleUpload}
        disabled={uploading || !file}
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '8px',
          border: 'none',
          background: uploading || !file ? '#bdbdbd' : '#4caf50',
          color: '#fff',
          fontWeight: 600,
          fontSize: 16,
          cursor: uploading || !file ? 'not-allowed' : 'pointer',
          marginBottom: uploading ? 18 : 0,
          boxShadow: uploading ? '0 2px 8px rgba(76,175,80,0.12)' : 'none',
          transition: 'background 0.2s'
        }}
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {uploading && (
        <div style={{ width: '100%', margin: '18px 0 8px 0' }}>
          <div style={{
            width: '100%',
            background: '#f1f1f1',
            borderRadius: '8px',
            height: '18px',
            overflow: 'hidden',
            boxShadow: '0 1px 4px rgba(0,0,0,0.04)'
          }}>
            <div style={{
              width: `${progress}%`,
              background: 'linear-gradient(90deg,#4caf50 60%,#81c784 100%)',
              height: '100%',
              transition: 'width 0.4s cubic-bezier(.4,0,.2,1)'
            }} />
          </div>
          <div style={{ textAlign: 'right', fontSize: 13, color: '#4caf50', fontWeight: 500, marginTop: 4 }}>
            {progress}%
          </div>
        </div>
      )}
      {s3Link && (
        <div style={{ width: '100%', marginTop: 18, textAlign: 'center' }}>
          <div style={{ fontSize: 15, color: '#388e3c', fontWeight: 500, marginBottom: 6 }}>Upload successful!</div>
          <a href={s3Link} target="_blank" rel="noopener noreferrer" style={{
            wordBreak: 'break-all',
            color: '#1976d2',
            fontSize: 13,
            textDecoration: 'underline'
          }}>{s3Link}</a>
        </div>
      )}
      {error && <div style={{ color: '#e53935', fontSize: 14, marginTop: 12 }}>{error}</div>}
    </div>
  );
}

export default S3Uploader;