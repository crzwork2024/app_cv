import React from 'react';

const ResumePreview = ({ pdfUrl }) => {
  return (
    {pdfUrl && (
      <iframe src={pdfUrl} width="800px" height="600px" />
    )}
  );
};

export default ResumePreview;
