import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = () => {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [optimizedResumeUrl, setOptimizedResumeUrl] = useState(null);

  const handleResumeChange = (event) => {
    setResume(event.target.files[0]);
  };

  const handleJobDescriptionChange = (event) => {
    setJobDescription(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('job_description', jobDescription);

    try {
      const response = await axios.post('/api/optimize', formData, {
        responseType: 'blob', // 接收 PDF 文件
      });

      // 创建 PDF 文件的 URL
      const url = URL.createObjectURL(response.data);
      setOptimizedResumeUrl(url);

    } catch (error) {
      console.error('Error optimizing resume:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept=".pdf" onChange={handleResumeChange} />
      <textarea value={jobDescription} onChange={handleJobDescriptionChange} />
      <button type="submit">生成优化简历</button>
      {optimizedResumeUrl && (
        <a href={optimizedResumeUrl} download="optimized_resume.pdf">
          下载优化简历
        </a>
      )}
    </form>
  );
};

export default UploadForm;
