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
import java.util.Map;
import java.net.Proxy.Type.*;

import android.os.AsyncTask;



public class UploadFileToServer extends AsyncTask<Map<String, String>, Integer, String> {
    @Override
    protected void onPreExecute() {
        // setting progress bar to zero
        super.onPreExecute();
    }

    @Override
    protected void onProgressUpdate(Integer... progress) {

    }

    @Override
    protected String doInBackground(Map<String, String>... postRequestDataMap) {
        return uploadFile(postRequestDataMap[0]);
    }

    @SuppressWarnings("deprecation")
    private String uploadFile(Map<String, String> postRequestDataMap) {
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

            final HttpPost httpPost = new HttpPost(endpoint);
            final File video_file = new File(postRequestDataMap.get("VIDEO_FILE_PATH"));
            final File csv_file = new File(postRequestDataMap.get("CSV_FILE_PATH"));
            MultipartEntityBuilder builder = MultipartEntityBuilder.create();
            builder.setMode(HttpMultipartMode.LEGACY);
            builder.addPart("file", new FileBody(video_file));
            builder.addPart("csv_file", new FileBody(csv_file));
            builder.addTextBody("client_id", postRequestDataMap.get("CLIENT_ID"));
            builder.addTextBody("session_prefix", postRequestDataMap.get("SESSION_PREFIX"));

//            JSONObject jsonObj = new JSONObject();
//            try{
//                jsonObj.put("client_id", postRequestDataMap.get("CLIENT_ID"));
//                jsonObj.put("session_prefix", postRequestDataMap.get("SESSION_PREFIX"));
//            }catch(Exception e){
//                e.printStackTrace();
//            }
//
//// Create the POST object and add the parameters
//            StringEntity sentity = new StringEntity(jsonObj.toString(), ContentType.APPLICATION_JSON, "UTF-8", false);
//
////                  postParameters = new ArrayList<NameValuePair>();
////            postParameters.add(new BasicNameValuePair("client_id", postRequestDataMap.get("CLIENT_ID")));
////            postParameters.add(new BasicNameValuePair("session_prefix",postRequestDataMap.get("SESSION_PREFIX") ));
//            httpPost.setEntity(sentity);
            HttpEntity entity = builder.build();
            httpPost.setEntity(entity);
            httpResponse = httpClient.execute(httpPost);
            statusCode = httpResponse.getCode();
            System.out.println("Response Status:" + statusCode);
            System.out.println("FILE UPLOADED");

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




