package com.googleresearch.capturesync;

import java.io.File;


import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.entity.mime.FileBody;
import org.apache.hc.client5.http.entity.mime.HttpMultipartMode;
import org.apache.hc.client5.http.entity.mime.MultipartEntityBuilder;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.HttpEntity;
import org.apache.hc.core5.http.HttpResponse;
import java.io.IOException;
import android.os.AsyncTask;



public class UploadFileToServer extends AsyncTask<String, Integer, String> {
    @Override
    protected void onPreExecute() {
        // setting progress bar to zero
        super.onPreExecute();
    }

    @Override
    protected void onProgressUpdate(Integer... progress) {

    }

    @Override
    protected String doInBackground(String... selectedFilePaths) {
        return uploadFile(selectedFilePaths);
    }

    @SuppressWarnings("deprecation")
    private String uploadFile(String... selectedFilePaths) {
        String responseString = "All Good";
        HttpResponse httpResponse;
        int statusCode;
        String response = "";


        try (final CloseableHttpClient httpClient = HttpClients.createDefault()) {
            final HttpPost httpPost = new HttpPost("http://192.168.5.1:5000/upload");

            final File video_file = new File(selectedFilePaths[0]);
            MultipartEntityBuilder builder = MultipartEntityBuilder.create();
            builder.setMode(HttpMultipartMode.LEGACY);
            builder.addPart("file", new FileBody(video_file));
            HttpEntity entity = builder.build();
            httpPost.setEntity(entity);
            httpResponse = httpClient.execute(httpPost);
            statusCode = httpResponse.getCode();
            System.out.println("Response Status:" + statusCode);
            System.out.println("FILE UPLOADED");

        } catch (IOException e) {
            responseString = e.toString();
        }
        return responseString;

    }

    @Override
    protected void onPostExecute(String result) {

        super.onPostExecute(result);
    }

}




