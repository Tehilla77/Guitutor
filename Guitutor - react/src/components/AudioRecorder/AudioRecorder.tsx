import React, { useRef, useState } from 'react';
import './AudioRecorder.scss';
import { useLocation } from 'react-router-dom';

const AudioRecorder: React.FC = () => {
  const [recordedUrl, setRecordedUrl] = useState<string>('');
  const mediaStream = useRef<MediaStream | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const [started, setStarted] = useState<boolean>(false)
  const [stopped, setStopped] = useState<boolean>(false)
  const location = useLocation();
  const songToLoad = location.state

  const startRecording = async (): Promise<void> => {
    try {
      // Request access to the microphone with the desired sample rate
      const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 44100,  // Set the desired sample rate
          echoCancellation: true,  // Optional: Enable echo cancellation
        },
      });

      mediaStream.current = stream;

      // Create a MediaRecorder instance
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm',  // You can also use 'audio/wav' or other supported formats
      });

      mediaRecorder.current.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) {
          chunks.current.push(e.data);
        }
      };

      mediaRecorder.current.onstop = async () => {
        const recordedBlob: Blob = new Blob(chunks.current, { type: 'audio/webm' });
        const url: string = URL.createObjectURL(recordedBlob);
        setRecordedUrl(url);
        chunks.current = [];

        // Send the Blob to the server
        await sendBlobToServer(recordedBlob);
      };

      mediaRecorder.current.start();
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = (): void => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach((track: MediaStreamTrack) => {
        track.stop();
      });
    }
  };

  const sendBlobToServer = async (blob: Blob): Promise<void> => {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');

    try {
      const response = await fetch('http://localhost:5000/upload_record', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log('Blob sent successfully!');
      } else {
        console.error('Failed to send blob');
      }
    } catch (error) {
      console.error('Error sending blob to server:', error);
    }
  };

  return (
    <div className="audio-recorder">
      <audio controls>
        <source src={songToLoad} type="audio/wav"></source>
      </audio>
      {recordedUrl != '' ? <audio controls src={recordedUrl} /> : ""}
      
      {
        !started ? <button className="start" onClick={() => { setStarted(true); startRecording() }}>Start Recording</button>
          : <button className="stop" onClick={() => { setStopped(true); stopRecording() }}>Stop Recording</button>
      }
      {
        stopped ? <button onClick={() => { setRecordedUrl(''); setStarted(false); setStopped(false) }}>Restart Recording</button> : ""
      }
    </div>
  );
};

export default AudioRecorder;

