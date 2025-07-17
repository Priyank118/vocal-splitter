import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Music, Mic, Download, X, LoaderCircle, FileAudio } from 'lucide-react';
import axios from 'axios';

// --- Main App Component ---
export default function App() {
    // --- State Management ---
    // 'idle': Waiting for file upload
    // 'uploading': File is being sent to the backend
    // 'processing': Backend is splitting the audio
    // 'success': Processing is complete, download links are available
    // 'error': An error occurred
    const [status, setStatus] = useState('idle');
    
    // Stores the selected file object
    const [file, setFile] = useState(null);
    
    // Stores the name of the uploaded file for display
    const [fileName, setFileName] = useState('');
    
    // Stores any error messages
    const [error, setError] = useState('');
    
    // Stores the download URLs received from the backend
    const [downloadUrls, setDownloadUrls] = useState({ vocalsUrl: '', musicUrl: '' });
    
    // Backend server URL
    const API_URL = 'http://localhost:5000';

    // --- Event Handlers ---

    /**
     * Handles the file upload process.
     * Validates the file and sends it to the backend server.
     */
    const handleUpload = async (selectedFile) => {
        if (!selectedFile) return;

        // Reset previous state
        setError('');
        setFile(selectedFile);
        setFileName(selectedFile.name);
        setStatus('uploading');

        // Create form data to send the file
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // Simulate a short delay for the 'uploading' state to be visible
            await new Promise(resolve => setTimeout(resolve, 500));
            
            setStatus('processing'); // Switch to processing state

            // Make the API call to the Flask backend
            const response = await axios.post(`${API_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // On success, update state with download links
            setDownloadUrls(response.data);
            setStatus('success');

        } catch (err) {
            // Handle errors from the backend
            const errorMessage = err.response?.data?.error || 'An unknown error occurred. Please try again.';
            setError(errorMessage);
            setStatus('error');
            // Reset file state after a delay to allow user to see the error
            setTimeout(() => {
                if (status === 'error') { // only reset if still in error state
                   handleReset();
                }
            }, 5000);
        }
    };

    /**
     * Triggered when a file is selected via the input element.
     */
    const onFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            handleUpload(selectedFile);
        }
    };

    /**
     * Resets the application to its initial state.
     */
    const handleReset = () => {
        setStatus('idle');
        setFile(null);
        setFileName('');
        setError('');
        setDownloadUrls({ vocalsUrl: '', musicUrl: '' });
    };

    /**
     * Handles the drag-and-drop functionality.
     */
    const onDrop = useCallback((event) => {
        event.preventDefault();
        event.stopPropagation();
        const droppedFile = event.dataTransfer.files[0];
        if (droppedFile) {
            handleUpload(droppedFile);
        }
    }, []);

    const onDragOver = (event) => {
        event.preventDefault();
        event.stopPropagation();
    };

    // --- UI Components ---

    /**
     * Memoized component for the initial file upload view.
     */
    const UploadComponent = useMemo(() => (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="w-full text-center"
        >
            <label
                htmlFor="audio-upload"
                onDrop={onDrop}
                onDragOver={onDragOver}
                className="relative flex flex-col items-center justify-center w-full h-64 px-4 transition-all duration-300 ease-in-out bg-gray-800/50 border-2 border-dashed rounded-2xl border-gray-600 hover:border-indigo-500 hover:bg-gray-800/70 cursor-pointer"
            >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <UploadCloud className="w-12 h-12 mb-4 text-gray-400 group-hover:text-indigo-400" />
                    <p className="mb-2 text-lg text-gray-300">
                        <span className="font-semibold text-indigo-400">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-sm text-gray-500">MP3, WAV, FLAC or M4A</p>
                </div>
                <input id="audio-upload" type="file" className="hidden" onChange={onFileChange} accept=".mp3,.wav,.flac,.m4a" />
            </label>
        </motion.div>
    ), [onDrop, onDragOver, onFileChange]);


    /**
     * Memoized component for displaying the processing state.
     */
    const ProcessingComponent = useMemo(() => (
        <motion.div
            key="processing"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="text-center w-full flex flex-col items-center justify-center h-64 bg-gray-800/50 rounded-2xl"
        >
            <LoaderCircle className="w-16 h-16 text-indigo-500 animate-spin mb-6" />
            <p className="text-xl font-medium text-gray-200 mb-2">Processing your song...</p>
            <p className="text-gray-400 max-w-sm">{fileName}</p>
            <p className="text-sm text-gray-500 mt-4">This may take a moment, please be patient.</p>
        </motion.div>
    ), [fileName]);

    /**
     * Memoized component for displaying download links and success message.
     */
    const SuccessComponent = useMemo(() => (
        <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, type: 'spring', stiffness: 120 }}
            className="w-full text-center p-8 bg-gray-800/50 rounded-2xl shadow-2xl"
        >
            <h2 className="text-2xl font-bold text-green-400 mb-4">Separation Complete!</h2>
            <p className="text-gray-300 mb-2">Your track is ready.</p>
            <div className="flex items-center justify-center bg-gray-900/50 p-3 rounded-lg mb-6 max-w-md mx-auto">
                <FileAudio className="w-5 h-5 mr-3 text-indigo-400" />
                <span className="text-gray-200 truncate">{fileName}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {/* Download Vocals Button */}
                <a
                    href={`${API_URL}${downloadUrls.vocalsUrl}`}
                    download
                    className="group flex items-center justify-center w-full px-6 py-4 text-lg font-semibold text-white bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg shadow-lg hover:scale-105 transition-transform duration-300 ease-in-out"
                >
                    <Mic className="w-6 h-6 mr-3 transition-transform duration-300 group-hover:rotate-[-12deg]" />
                    Download Vocals
                </a>
                {/* Download Music Button */}
                <a
                    href={`${API_URL}${downloadUrls.musicUrl}`}
                    download
                    className="group flex items-center justify-center w-full px-6 py-4 text-lg font-semibold text-white bg-gradient-to-r from-teal-500 to-cyan-600 rounded-lg shadow-lg hover:scale-105 transition-transform duration-300 ease-in-out"
                >
                    <Music className="w-6 h-6 mr-3 transition-transform duration-300 group-hover:rotate-[12deg]" />
                    Download Music
                </a>
            </div>
            
            <button
                onClick={handleReset}
                className="text-gray-400 hover:text-white transition-colors duration-200"
            >
                Process another song
            </button>
        </motion.div>
    ), [fileName, downloadUrls, API_URL]);
    
    /**
     * Memoized component for displaying error messages.
     */
    const ErrorComponent = useMemo(() => (
         <motion.div
            key="error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="w-full p-6 bg-red-900/30 border border-red-500 rounded-2xl text-center"
        >
            <h3 className="text-xl font-semibold text-red-400 mb-2">An Error Occurred</h3>
            <p className="text-red-300">{error}</p>
             <button
                onClick={handleReset}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
                Try Again
            </button>
        </motion.div>
    ), [error]);


    // --- Main Render ---
    return (
        <div className="min-h-screen bg-gray-900 text-white font-sans flex flex-col items-center justify-center p-4 overflow-hidden">
            {/* Background Gradient Blobs */}
            <div className="absolute top-0 left-0 w-72 h-72 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob"></div>
            <div className="absolute top-0 right-0 w-72 h-72 bg-teal-500 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob animation-delay-2000"></div>
            <div className="absolute bottom-20 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob animation-delay-4000"></div>

            <main className="relative z-10 flex flex-col items-center justify-center w-full max-w-2xl mx-auto">
                {/* Header */}
                <header className="text-center mb-10">
                    <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-indigo-400 to-teal-400">
                        Vocal Splitter AI
                    </h1>
                    <p className="mt-3 text-lg text-gray-400">
                        Separate any song into vocals and music with one click.
                    </p>
                </header>

                {/* Main Content Area */}
                <div className="w-full">
                    <AnimatePresence mode="wait">
                        {status === 'idle' && UploadComponent}
                        {(status === 'uploading' || status === 'processing') && ProcessingComponent}
                        {status === 'success' && SuccessComponent}
                        {status === 'error' && ErrorComponent}
                    </AnimatePresence>
                </div>
            </main>
            
            {/* Footer */}
            <footer className="absolute bottom-4 text-center text-gray-600 text-sm">
                <p>Powered by Spleeter & React. Crafted with ❤️.</p>
            </footer>
        </div>
    );
}

// Add this CSS to your global stylesheet (e.g., index.css) for the blob animations
/*
@keyframes blob {
	0% {
		transform: translate(0px, 0px) scale(1);
	}
	33% {
		transform: translate(30px, -50px) scale(1.1);
	}
	66% {
		transform: translate(-20px, 20px) scale(0.9);
	}
	100% {
		transform: translate(0px, 0px) scale(1);
	}
}

.animate-blob {
	animation: blob 7s infinite;
}

.animation-delay-2000 {
	animation-delay: 2s;
}

.animation-delay-4000 {
	animation-delay: 4s;
}
*/
