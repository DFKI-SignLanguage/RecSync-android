/*
 * Copyright 2021 Mobile Robotics Lab. at Skoltech.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.googleresearch.capturesync;

import static android.hardware.camera2.CameraDevice.TEMPLATE_PREVIEW;
import static android.hardware.camera2.CameraDevice.TEMPLATE_MANUAL;
import static android.hardware.camera2.CameraMetadata.CONTROL_AE_MODE_OFF;

import static android.hardware.camera2.CameraMetadata.CONTROL_AF_MODE_OFF;
import static android.hardware.camera2.CameraMetadata.CONTROL_AF_TRIGGER_CANCEL;

import static android.hardware.camera2.CameraMetadata.CONTROL_AWB_MODE_AUTO;
import static android.hardware.camera2.CameraMetadata.CONTROL_MODE_AUTO;
import static android.hardware.camera2.CaptureRequest.CONTROL_AE_MODE;
import static android.hardware.camera2.CaptureRequest.CONTROL_AF_MODE;
import static android.hardware.camera2.CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE;
import static android.hardware.camera2.CaptureRequest.CONTROL_AF_TRIGGER;
import static android.hardware.camera2.CaptureRequest.CONTROL_AWB_MODE;
import static android.hardware.camera2.CaptureRequest.CONTROL_MODE;
import static android.hardware.camera2.CaptureRequest.LENS_FOCUS_DISTANCE;
import static android.hardware.camera2.CaptureRequest.SENSOR_EXPOSURE_TIME;
import static android.hardware.camera2.CaptureRequest.SENSOR_SENSITIVITY;

import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CaptureRequest;
import android.view.Surface;
import android.widget.Toast;

import com.googleresearch.capturesync.ImageMetadataSynchronizer.CaptureRequestTag;
import java.util.ArrayList;
import java.util.List;

/** Helper class for creating common {@link CaptureRequest.Builder} instances. */
public class CaptureRequestFactory {

  private final CameraDevice device;

  public CaptureRequestFactory(CameraDevice camera) {
    device = camera;
  }

  /**
   * Makes a {@link CaptureRequest.Builder} for the viewfinder preview. This always adds the
   * viewfinder.
   */
  public CaptureRequest.Builder makePreview(
          Surface viewfinderSurface,
          List<Surface> imageSurfaces,
          long sensorExposureTimeNs,
          int sensorSensitivity,
          boolean wantAutoExp, boolean enableFocus)
          throws CameraAccessException {

    CaptureRequest.Builder builder = device.createCaptureRequest(TEMPLATE_PREVIEW);
    if (wantAutoExp) {
      builder.set(CONTROL_AE_MODE, CONTROL_AWB_MODE_AUTO);
    } else {
      // Manually set exposure and sensitivity using UI sliders on the leader.
      builder.set(CONTROL_AE_MODE, CONTROL_AE_MODE_OFF);
      builder.set(SENSOR_EXPOSURE_TIME, sensorExposureTimeNs);
      builder.set(SENSOR_SENSITIVITY, sensorSensitivity);
    }
    builder.set(CONTROL_AF_TRIGGER, CONTROL_AF_TRIGGER_CANCEL);
    builder.set(CONTROL_AF_MODE, CONTROL_AF_MODE_OFF);
    // Auto white balance used, these could be locked and sent from the leader instead.
    builder.set(CONTROL_AWB_MODE, CONTROL_AWB_MODE_AUTO);

    if (viewfinderSurface != null) {
      builder.addTarget(viewfinderSurface);
    }
    List<Integer> targetIndices = new ArrayList<>();
    for (int i = 0; i < imageSurfaces.size(); i++) {
      builder.addTarget(imageSurfaces.get(i));
      targetIndices.add(i);
    }
    builder.setTag(new CaptureRequestTag(targetIndices, null));
    return builder;
  }


  /**
   * An alternative capture request for video,
   * includes everything from preview + mediaRecorder
   */
  public CaptureRequest.Builder makeVideo(
          Surface recorderSurface,
          Surface viewfinderSurface,
          List<Surface> imageSurfaces,
          long sensorExposureTimeNs,
          int sensorSensitivity,
          boolean wantAutoExp, boolean enableFocus)
          throws CameraAccessException {
    CaptureRequest.Builder builder = makePreview(viewfinderSurface, imageSurfaces, sensorExposureTimeNs, sensorSensitivity, wantAutoExp, enableFocus);
    // Add recorder surface
    if (recorderSurface != null) {
      builder.addTarget(recorderSurface);
    }
    return builder;
  }


  public CaptureRequest.Builder makeFrameInjectionRequest(
          long desiredExposureTimeNs, List<Surface> imageSurfaces) throws CameraAccessException {

    CaptureRequest.Builder builder = device.createCaptureRequest(TEMPLATE_PREVIEW);
    builder.set(CONTROL_MODE, CONTROL_MODE_AUTO);
    builder.set(CONTROL_AE_MODE, CONTROL_AE_MODE_OFF);
    builder.set(SENSOR_EXPOSURE_TIME, desiredExposureTimeNs);
    builder.set(CONTROL_AF_TRIGGER, CONTROL_AF_TRIGGER_CANCEL);
    builder.set(CONTROL_AF_MODE, CONTROL_AF_MODE_OFF);
    // TODO: Inserting frame duration directly would be more accurate than inserting exposure since
    // {@code frame duration ~ exposure + variable overhead}. However setting frame duration may not
    // be supported on many android devices, so we use exposure time here.

    List<Integer> targetIndices = new ArrayList<>();
    for (int i = 0; i < imageSurfaces.size(); i++) {
      builder.addTarget(imageSurfaces.get(i));
      targetIndices.add(i);
    }
    builder.setTag(new CaptureRequestTag(targetIndices, PhaseAlignController.INJECT_FRAME));

    return builder;
  }
}
