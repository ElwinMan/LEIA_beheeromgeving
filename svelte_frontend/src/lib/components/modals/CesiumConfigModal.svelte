<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { CesiumConfiguration } from '$lib/types/digitalTwinAssociation';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  interface Props {
    config?: CesiumConfiguration;
    title?: string;
  }

  let { config = {}, title = 'Configureer Cesium Terrain Instellingen' }: Props = $props();

  const dispatch = createEventDispatcher<{
    save: CesiumConfiguration;
    cancel: void;
  }>();

  let modalElement: HTMLDialogElement;
  let localConfig = $state<CesiumConfiguration>({ ...config });

  // Date/time handling
  let dateTimeInputType = $state<'timestamp' | 'datetime'>('datetime');
  let humanDateTime = $state('');

  // Convert Unix timestamp to human-readable date
  function timestampToDateTime(timestamp: number): string {
    if (!timestamp) return '';
    const date = new Date(timestamp * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  // Convert human-readable date to Unix timestamp
  function dateTimeToTimestamp(dateTimeStr: string): number {
    if (!dateTimeStr) return 0;
    const date = new Date(dateTimeStr);
    return Math.floor(date.getTime() / 1000);
  }

  // Update timestamp when human date changes
  function handleDateTimeChange(event: Event) {
    const target = event.target as HTMLInputElement;
    humanDateTime = target.value;
    if (humanDateTime) {
      localConfig.dateTime = dateTimeToTimestamp(humanDateTime);
    }
  }

  // Update human date when timestamp changes
  function handleTimestampChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const timestamp = parseInt(target.value);
    if (!isNaN(timestamp)) {
      localConfig.dateTime = timestamp;
      humanDateTime = timestampToDateTime(timestamp);
    }
  }

  export function showModal() {
    // Initialize modal with provided config, applying defaults for missing values
    const safeConfig = config || {};
    localConfig = { 
      // Date and time settings
      dateTime: safeConfig.dateTime ?? 1657450800, // 10-07-2022 11:00:00
      
      // Visual quality and rendering
      shadows: safeConfig.shadows ?? false,
      fxaa: safeConfig.fxaa ?? false,
      msaa: safeConfig.msaa ?? 4,
      lighting: safeConfig.lighting ?? true,
      animate: safeConfig.animate ?? false,
      resolutionScale: safeConfig.resolutionScale ?? 1.0,
      
      // Level of detail and performance
      maximumScreenSpaceError: safeConfig.maximumScreenSpaceError ?? 1.5,
      
      // Atmospheric effects
      groundAtmosphere: safeConfig.groundAtmosphere ?? true,
      fog: safeConfig.fog ?? true,
      highDynamicRange: safeConfig.highDynamicRange ?? true,
      
      // Point cloud settings
      pointCloudAttenuation: safeConfig.pointCloudAttenuation ?? true,
      pointCloudAttenuationMaximum: safeConfig.pointCloudAttenuationMaximum ?? 0,
      pointCloudAttenuationErrorScale: safeConfig.pointCloudAttenuationErrorScale ?? 1,
      pointCloudAttenuationBaseResolution: safeConfig.pointCloudAttenuationBaseResolution ?? 0,
      pointCloudEDL: safeConfig.pointCloudEDL ?? true,
      pointCloudEDLStrength: safeConfig.pointCloudEDLStrength ?? 1,
      pointCloudEDLRadius: safeConfig.pointCloudEDLRadius ?? 1,
      
      // Globe settings
      globeOpacity: safeConfig.globeOpacity ?? 100,
      
      // Debug and development
      showMouseCoordinates: safeConfig.showMouseCoordinates ?? false,
      showCameraPosition: safeConfig.showCameraPosition ?? false,
      showLoadingWidget: safeConfig.showLoadingWidget ?? false
    };
    
    // Initialize date/time values
    if (localConfig.dateTime) {
      humanDateTime = timestampToDateTime(localConfig.dateTime);
    }
    
    modalElement?.showModal();
  }

  export function closeModal() {
    modalElement?.close();
  }

  function handleSave() {
    dispatch('save', localConfig);
    closeModal();
  }

  function handleCancel() {
    dispatch('cancel');
    closeModal();
  }
</script>

<dialog bind:this={modalElement} class="modal">
  <div class="modal-box w-11/12 max-w-6xl">
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
    </form>
    
    <h3 class="text-lg font-bold mb-4">{title}</h3>
    
    <div class="space-y-6">
      <!-- Date and Time Settings -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">Sun Position</h4>
        
        <div class="form-control">
          <label class="label" for="date-time">
            <div class="flex items-center gap-2">
              <span class="label-text">Date and Time</span>
              <HelpTooltip tip="Date and time, determines the sun position and lighting in the scene" />
            </div>
          </label>
          
          <!-- Input type selector -->
          <div class="flex gap-2 mb-3">
            <button 
              type="button"
              class="btn btn-sm {dateTimeInputType === 'datetime' ? 'btn-primary' : 'btn-outline'}"
              onclick={() => dateTimeInputType = 'datetime'}
            >
              Date & Time
            </button>
            <button 
              type="button"
              class="btn btn-sm {dateTimeInputType === 'timestamp' ? 'btn-primary' : 'btn-outline'}"
              onclick={() => dateTimeInputType = 'timestamp'}
            >
              Unix Timestamp
            </button>
          </div>
          
          {#if dateTimeInputType === 'datetime'}
            <!-- Human-readable date/time input -->
            <input 
              id="date-time-human"
              type="datetime-local" 
              class="input input-bordered" 
              value={humanDateTime}
              oninput={handleDateTimeChange}
              placeholder="2022-07-10T11:00"
            />
            <div class="label">
              <span class="label-text-alt">Human-readable date and time input</span>
            </div>
          {:else}
            <!-- Unix timestamp input -->
            <input 
              id="date-time-timestamp"
              type="number" 
              class="input input-bordered" 
              value={localConfig.dateTime}
              oninput={handleTimestampChange}
              placeholder="1657450800"
            />
            <div class="label">
              <span class="label-text-alt">Unix timestamp (seconds since epoch)</span>
            </div>
          {/if}
          
          <div class="label">
            <span class="label-text-alt">Default: 1657450800 (10-07-2022 11:00:00)</span>
          </div>
        </div>
      </div>

      <!-- Visual Quality & Rendering -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">Visual Quality & Rendering</h4>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Shadows</span>
                <HelpTooltip tip="Shadows enabled/disabled" position="right"/>
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.shadows}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">FXAA</span>
                <HelpTooltip tip="FXAA enabled" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.fxaa}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Lighting</span>
                <HelpTooltip tip="Enable lighting the globe with the scene's light source" position="right" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.lighting}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Animate</span>
                <HelpTooltip tip="Enable when displaying animated models else animations only update when the viewer refreshes it's view such as when panning/zooming" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.animate}
              />
            </label>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-4">
          <div class="form-control">
            <label class="label" for="msaa">
              <div class="flex items-center gap-2">
                <span class="label-text">MSAA Samples</span>
                <HelpTooltip tip="MSAA samples" position="right"/>
              </div>
            </label>
            <input 
              id="msaa"
              type="number" 
              class="input input-bordered" 
              bind:value={localConfig.msaa}
              placeholder="4"
              min="1"
              max="16"
            />
          </div>

          <div class="form-control">
            <label class="label" for="resolution-scale">
              <div class="flex items-center gap-2">
                <span class="label-text">Resolution Scale</span>
                <HelpTooltip tip="Gets or sets a scaling factor for rendering resolution. Values less than 1.0 can improve performance on less powerful devices while values greater than 1.0 will render at a higher resolution and then scale down, resulting in improved visual fidelity" />
              </div>
            </label>
            <input 
              id="resolution-scale"
              type="number" 
              step="0.1"
              min="0.1"
              max="3.0"
              class="input input-bordered" 
              bind:value={localConfig.resolutionScale}
              placeholder="1.0"
            />
          </div>
        </div>

        <div class="form-control mt-4">
          <label class="label" for="max-screen-space-error">
            <div class="flex items-center gap-2">
              <span class="label-text">Maximum Screen Space Error</span>
              <HelpTooltip tip="The maximum screen space error used to drive level of detail refinement for 3D tile layers" position="right" />
            </div>
            <span class="label-text-alt">For 3D tile layers</span>
          </label>
          <input 
            id="max-screen-space-error"
            type="number" 
            step="0.1"
            min="0.1"
            max="32"
            class="input input-bordered" 
            bind:value={localConfig.maximumScreenSpaceError}
            placeholder="1.5"
          />
        </div>
      </div>

      <!-- Atmospheric Effects -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">Atmospheric Effects</h4>
        
        <div class="grid grid-cols-3 gap-4">
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Ground Atmosphere</span>
                <HelpTooltip tip="Ground atmosphere enabled" position="right" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.groundAtmosphere}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Fog</span>
                <HelpTooltip tip="Fog enabled" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.fog}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">High Dynamic Range</span>
                <HelpTooltip tip="HDR enabled" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.highDynamicRange}
              />
            </label>
          </div>
        </div>
      </div>

      <!-- Point Cloud Settings -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">Point Cloud Settings</h4>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Point Cloud Attenuation</span>
                <HelpTooltip tip="3D Tile Point Cloud Attenuation enabled, Perform point attenuation based on geometric error" position="right" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.pointCloudAttenuation}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Eye Dome Lighting (EDL)</span>
                <HelpTooltip tip="Eye Dome Lighting enabled, Use eye dome lighting when drawing with point attenuation Requires support for EXT_frag_depth, OES_texture_float, and WEBGL_draw_buffers extensions in WebGL 1.0, otherwise eye dome lighting is ignored" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.pointCloudEDL}
              />
            </label>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-4">
          <div class="form-control">
            <label class="label" for="pc-attenuation-max">
              <div class="flex items-center gap-2">
                <span class="label-text">Attenuation Maximum (px)</span>
                <HelpTooltip tip="3D Tile Point Cloud Maximum point attenuation in pixels. If undefined, the Cesium3DTileset's maximumScreenSpaceError will be used" position="right" />
              </div>
            </label>
            <input 
              id="pc-attenuation-max"
              type="number" 
              class="input input-bordered" 
              bind:value={localConfig.pointCloudAttenuationMaximum}
              placeholder="0"
              min="0"
            />
          </div>

          <div class="form-control">
            <label class="label" for="pc-error-scale">
              <div class="flex items-center gap-2">
                <span class="label-text">Error Scale</span>
                <HelpTooltip tip="Scale to be applied to the geometric error before computing attenuation" />
              </div>
            </label>
            <input 
              id="pc-error-scale"
              type="number" 
              step="0.1"
              class="input input-bordered" 
              bind:value={localConfig.pointCloudAttenuationErrorScale}
              placeholder="1"
              min="0"
            />
          </div>

          <div class="form-control">
            <label class="label" for="pc-base-resolution">
              <div class="flex items-center gap-2">
                <span class="label-text">Base Resolution (m)</span>
                <HelpTooltip tip="Average base resolution for the dataset in meters. Used in place of geometric error when the geometric error is 0. If undefined, an approximation will be computed for each tile that has a geometric error of 0" position="right" />
              </div>
            </label>
            <input 
              id="pc-base-resolution"
              type="number" 
              class="input input-bordered" 
              bind:value={localConfig.pointCloudAttenuationBaseResolution}
              placeholder="0"
              min="0"
            />
          </div>

          <div class="form-control">
            <label class="label" for="pc-edl-strength">
              <div class="flex items-center gap-2">
                <span class="label-text">EDL Strength</span>
                <HelpTooltip tip="Eye dome lighting strength (apparent contrast)" />
              </div>
            </label>
            <input 
              id="pc-edl-strength"
              type="number" 
              step="0.1"
              class="input input-bordered" 
              bind:value={localConfig.pointCloudEDLStrength}
              placeholder="1"
              min="0"
            />
          </div>

          <div class="form-control">
            <label class="label" for="pc-edl-radius">
              <div class="flex items-center gap-2">
                <span class="label-text">EDL Radius</span>
                <HelpTooltip tip="Thickness of contours from eye dome lighting" position="right" />
              </div>
            </label>
            <input 
              id="pc-edl-radius"
              type="number" 
              step="0.1"
              class="input input-bordered" 
              bind:value={localConfig.pointCloudEDLRadius}
              placeholder="1"
              min="0"
            />
          </div>
        </div>
      </div>

      <!-- Globe Settings -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">Globe Settings</h4>
        
        <div class="form-control">
          <label class="label" for="globe-opacity">
            <div class="flex items-center gap-2">
              <span class="label-text">Globe Opacity</span>
              <HelpTooltip tip="Opacity percentage of the globe" position="right" />
            </div>
            <span class="label-text-alt">{localConfig.globeOpacity}%</span>
          </label>
          <input 
            id="globe-opacity"
            type="range" 
            min="0" 
            max="100" 
            step="1" 
            class="range range-primary" 
            bind:value={localConfig.globeOpacity}
          />
        </div>
      </div>

      <!-- User Interface Options -->
      <div class="card bg-base-200 p-4">
        <h4 class="text-md font-semibold mb-3">User Interface Options</h4>
        
        <div class="grid grid-cols-3 gap-4">
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Show Mouse Coordinates</span>
                <HelpTooltip tip="Debug window in viewer to show coordinates for mouse position" position="right" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.showMouseCoordinates}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Show Camera Position</span>
                <HelpTooltip tip="Debug window to show the current camera position, updates on move" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.showCameraPosition}
              />
            </label>
          </div>

          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-center gap-2">
                <span class="label-text">Show Loading Widget</span>
                <HelpTooltip tip="Show a small bar on the bottom of the viewer showing the loading progress of layers" />
              </div>
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                bind:checked={localConfig.showLoadingWidget}
              />
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-action">
      <button type="button" class="btn btn-ghost" onclick={handleCancel}>Cancel</button>
      <button type="button" class="btn btn-primary" onclick={handleSave}>Save Configuration</button>
    </div>
  </div>
</dialog>
