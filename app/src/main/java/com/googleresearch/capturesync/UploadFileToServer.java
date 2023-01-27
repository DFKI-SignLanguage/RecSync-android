package com.googleresearch.capturesync;

import java.io.File;


import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.entity.UrlEncodedFormEntity;
import org.apache.hc.client5.http.entity.mime.FileBody;
import org.apache.hc.client5.http.entity.mime.HttpMultipartMode;
import org.apache.hc.client5.http.entity.mime.MultipartEntityBuilder;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.ContentType;
import org.apache.hc.core5.http.HttpEntity;
import org.apache.hc.core5.http.HttpResponse;
import org.apache.hc.core5.http.NameValuePair;
import org.apache.hc.core5.http.io.entity.StringEntity;
import org.apache.hc.core5.http.message.BasicNameValuePair;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.net.Proxy.Type.*;

import android.os.AsyncTask;



public class UploadFileToServer extends AsyncTask<List<Map<String, String>>, Integer, String> {
    @Override
    protected void onPreExecute() {
        // setting progress bar to zero
        super.onPreExecute();
    }

    @Override
    protected void onProgressUpdate(Integer... progress) {

    }

    @Override
    protected String doInBackground(List<Map<String, String>>... postRequestDataMap) {
        return uploadFile(postRequestDataMap[0]);
    }

    @SuppressWarnings("deprecation")
    private String uploadFile(List<Map<String, String>> postRequestDataList) {
        String responseString = "All Good";
        HttpResponse httpResponse;
        ArrayList<NameValuePair> postParameters;
        int statusCode;
        String response = "";


        try (final CloseableHttpClient httpClient = HttpClients.createDefault()) {
            String endpoint = "http://192.168.5.1:5000/upload";
//            if(postRequestDataMap.get("API_ENDPOINT") != ""){
//                endpoint = postRequestDataMap.get("API_ENDPOINT");
//            }
            Map<String, String> postRequestDataMap ;
            for (int j=0; j<postRequestDataList.size(); j++){
                postRequestDataMap = postRequestDataList.get(j);
                final HttpPost httpPost = new HttpPost(endpoint);
                final File video_file = new File(postRequestDataMap.get("VIDEO_FILE_PATH"));
                final File csv_file = new File(postRequestDataMap.get("CSV_FILE_PATH"));
                MultipartEntityBuilder builder = MultipartEntityBuilder.create();
                builder.setMode(HttpMultipartMode.LEGACY);
                builder.addPart("file", new FileBody(video_file));
                builder.addPart("csv_file", new FileBody(csv_file));
                builder.addTextBody("client_id", postRequestDataMap.get("CLIENT_ID"));
                builder.addTextBody("session_prefix", postRequestDataMap.get("SESSION_PREFIX"));

                HttpEntity entity = builder.build();
                httpPost.setEntity(entity);
                httpResponse = httpClient.execute(httpPost);
                statusCode = httpResponse.getCode();
                System.out.println("Response Status:" + statusCode);
                System.out.println("FILE UPLOADED");

            }


        } catch (IOException e) {
            e.printStackTrace();
        }
        return responseString;

    }

    @Override
    protected void onPostExecute(String result) {

        super.onPostExecute(result);
    }

}




