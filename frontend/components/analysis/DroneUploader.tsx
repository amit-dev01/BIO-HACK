"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileImage, Trash2, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface DroneUploaderProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export function DroneUploader({ onFileSelect, selectedFile }: DroneUploaderProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        onFileSelect(file);
        if (file.type.startsWith("image/")) {
          const url = URL.createObjectURL(file);
          setPreviewUrl(url);
        } else {
          setPreviewUrl(null);
        }
      }
    },
    [onFileSelect]
  );

  const removeFile = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    onFileSelect(null);
  }, [previewUrl, onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024, // 500MB
    accept: {
      "image/tiff": [".tif", ".tiff"],
      "image/jp2": [".jp2"],
      "image/png": [".png"],
    },
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? "border-green-500 bg-green-50/50"
              : "border-gray-200 hover:border-green-400 bg-gray-50/50 hover:bg-gray-50"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center">
            <div className="p-3 bg-white rounded-full shadow-sm border border-gray-100 mb-3 text-green-600">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-gray-800">
              {isDragActive
                ? "Drop the drone orthomosaic here"
                : "Drag & drop a drone image, or click to browse"}
            </p>
            <p className="text-xs text-gray-400 mt-1 mb-3">
              Max file size: 500MB
            </p>

            <div className="flex flex-wrap gap-1.5 justify-center">
              <Badge variant="outline" className="text-[10px] bg-white text-gray-600">
                .tif
              </Badge>
              <Badge variant="outline" className="text-[10px] bg-white text-gray-600">
                .tiff
              </Badge>
              <Badge variant="outline" className="text-[10px] bg-white text-gray-600">
                .jp2
              </Badge>
              <Badge variant="outline" className="text-[10px] bg-white text-gray-600">
                .png
              </Badge>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl border border-green-200 bg-green-50/40 flex items-center justify-between gap-3 animate-in fade-in">
          <div className="flex items-center gap-3 overflow-hidden">
            {previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewUrl}
                alt="Uploaded Preview"
                className="w-12 h-12 object-cover rounded-lg border border-green-300 shrink-0"
              />
            ) : (
              <div className="w-12 h-12 rounded-lg bg-green-100 border border-green-200 flex items-center justify-center shrink-0 text-green-700">
                <FileImage className="w-6 h-6" />
              </div>
            )}
            <div className="overflow-hidden">
              <div className="flex items-center gap-1.5">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {selectedFile.name}
                </p>
                <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0" />
              </div>
              <p className="text-xs text-gray-500 font-mono">
                {formatFileSize(selectedFile.size)} • Ready for sub-canopy fusion
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={removeFile}
            className="p-2 text-gray-400 hover:text-red-600 hover:bg-white rounded-lg transition-colors shrink-0"
            title="Remove uploaded image"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

export default DroneUploader;

