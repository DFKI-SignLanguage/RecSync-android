package com.googleresearch.capturesync;


import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import android.os.AsyncTask;
import android.util.Log;

public class RemoteFileUpload extends  AsyncTask<String, Integer, Boolean> {

    @Override
    protected Boolean doInBackground(String ... selectedFilePaths) {
        HttpURLConnection conn = null;
        DataOutputStream os = null;
        DataInputStream inputStream = null;

        String urlServer = "http://192.168.5.1:5000/upload";

        String lineEnd = "\r\n";
        String twoHyphens = "--";
        String boundary = "*****";
        int bytesRead, bytesAvailable, bufferSize, bytesUploaded = 0;
        byte[] buffer;
        int maxBufferSize = 2 * 1024 * 1024;

        String uploadname = "test_file";

        try {
            FileInputStream fis = new FileInputStream(new File(selectedFilePaths[0]));
            System.out.println("FILE_PATH: " + selectedFilePaths[0]);
            URL url = new URL(urlServer);
            conn = (HttpURLConnection) url.openConnection();
            conn.setChunkedStreamingMode(maxBufferSize);

            // POST settings.
            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setUseCaches(false);
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("Content-Type", "multipart/form-data;  boundary=" + boundary);
            conn.setRequestProperty("Name", "Testing request");
            conn.connect();

            os = new DataOutputStream(conn.getOutputStream());
            os.writeBytes(twoHyphens + boundary + lineEnd);
            os.writeBytes("Content-Disposition: form-data; name=\"uploadedfile\";filename=\"" + uploadname + "\"" + lineEnd);
            os.writeBytes(lineEnd);

            bytesAvailable = fis.available();
            System.out.println("available: " + String.valueOf(bytesAvailable));
            bufferSize = Math.min(bytesAvailable, maxBufferSize);
            buffer = new byte[bufferSize];

            bytesRead = fis.read(buffer, 0, bufferSize);
            bytesUploaded += bytesRead;
            while (bytesRead > 0) {
                os.write(buffer, 0, bufferSize);
                bytesAvailable = fis.available();
                bufferSize = Math.min(bytesAvailable, maxBufferSize);
                buffer = new byte[bufferSize];
                bytesRead = fis.read(buffer, 0, bufferSize);
                bytesUploaded += bytesRead;
            }
            System.out.println("uploaded: " + String.valueOf(bytesUploaded));
            os.writeBytes(lineEnd);
            os.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

            // Responses from the server (code and message)
            conn.setConnectTimeout(2000); // allow 2 seconds timeout.
            int rcode = conn.getResponseCode();
            if (rcode == 200){
                System.out.println("Success");
            }
            fis.close();
            os.flush();
            os.close();

        } catch (Exception ex) {
            ex.printStackTrace();
            //return false;
        }
        return null;
    }

    @Override
    protected void onProgressUpdate(Integer... values) {
        Log.i("PROGRESSO", values[0]+"");

        //super.onProgressUpdate(values);
    }
    @Override
    protected void onPostExecute(Boolean result) {
        super.onPostExecute(result);
    }

}