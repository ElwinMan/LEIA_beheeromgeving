<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import type { Tool } from '$lib/types/tool';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  const dispatch = createEventDispatcher();

  export let tool: Tool & { enabled: boolean; settings?: Record<string, any> };
  export let toolSettingTooltips: Record<string, string>;

  let featureInfoFields: { field: string; handler: string }[] = [];

  // Sync feature info fields when component mounts or tool changes
  $: if (tool) {
    syncFeatureInfoFields();
  }

  function syncFeatureInfoFields() {
    if (tool.name?.toLowerCase() === 'featureinfo' && tool.enabled) {
      if (Array.isArray(tool.settings?.fields)) {
        featureInfoFields = tool.settings.fields.map((f: any) => ({ 
          field: f.field || '', 
          handler: f.handler || 'image' 
        }));
      } else {
        featureInfoFields = [];
      }
    } else {
      featureInfoFields = [];
    }
  }

  function toggleToolSetting(settingKey: string) {
    dispatch('toggleSetting', { toolId: tool.id, settingKey });
  }

  function updateToolTextSetting(settingKey: string, value: string) {
    dispatch('updateTextSetting', { toolId: tool.id, settingKey, value });
  }

  function updateFeatureInfoFields(newFields: { field: string; handler: string }[]) {
    featureInfoFields = newFields;
    dispatch('updateFeatureInfoFields', { fields: newFields });
  }

  function updateLayerLibraryConnectors(connectors: any[]) {
    dispatch('updateConnectors', { toolId: tool.id, connectors });
  }

  function getConfigurableBooleanSettings() {
    if (!tool || !tool.content?.settings) return [];
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'boolean')
      .map(([key, value]) => ({
        key,
        value: tool.settings?.[key] ?? value,
        label: key
      }));
  }

  function getConfigurableTextSettings() {
    if (!tool || !tool.content?.settings) return [];
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'string')
      .map(([key, value]) => ({
        key,
        value: tool.settings?.[key] ?? value,
        label: key,
        multiline: key === 'description'
      }));
  }

  function getLayerLibraryConnectors(): any[] {
    if (!tool || !tool.settings) return [];
    return tool.settings?.connectors ?? [];
  }
</script>

{#if tool}
<div class="space-y-4">
  <!-- Boolean Settings -->
  {#if getConfigurableBooleanSettings().length > 0}
    {@const configurableBooleanSettings = getConfigurableBooleanSettings()}
    <div class="space-y-3">
      <div class="flex items-center space-x-2">
        <div class="w-1 h-4 bg-secondary rounded"></div>
        <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide">Opties</h5>
      </div>
      <div class="space-y-2 pl-3">
        {#each configurableBooleanSettings as setting}
          <label class="flex cursor-pointer items-center space-x-3 p-2 rounded-md hover:bg-base-50 transition-colors select-none">
            <input
              type="checkbox"
              checked={setting.value}
              on:change={() => toggleToolSetting(setting.key)}
              class="checkbox checkbox-sm checkbox-secondary"
            />
            <span class="text-sm font-medium flex items-center gap-2">
              {setting.label}
              <span class="normal-case">
                <HelpTooltip tip={toolSettingTooltips[setting.key]} />
              </span>
            </span>
          </label>
        {/each}
      </div>
    </div>
  {/if}
  
  <!-- Text Settings -->
  {#if getConfigurableTextSettings().length > 0}
    {@const configurableTextSettings = getConfigurableTextSettings()}
    <div class="space-y-3">
      <div class="flex items-center space-x-2">
        <div class="w-1 h-4 bg-primary rounded"></div>
        <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide">Tekst instellingen</h5>
      </div>
      <div class="space-y-3 pl-3">
        {#each configurableTextSettings as setting}
          <div class="form-control">
            <label class="label flex items-center gap-2" for="tool-{tool.id}-{setting.key}">
              <span class="label-text text-sm font-medium">{setting.label}</span>
              <span class="normal-case">
                <HelpTooltip tip={toolSettingTooltips[setting.key]} />
              </span>
            </label>
            {#if tool.name?.toLowerCase() === 'geocoder' && setting.key === 'name'}
              <select
                id="tool-{tool.id}-{setting.key}"
                class="select select-bordered select-s w-full focus:border-primary"
                value={setting.value}
                on:change={(e) => updateToolTextSetting(setting.key, (e.target as HTMLSelectElement)?.value || '')}
              >
                <option value="locatieserver">locatieserver (Nederland)</option>
                <option value="geolocation">geolocation (België)</option>
                <option value="nominatim">nominatim (Wereldwijd)</option>
              </select>
            {:else if setting.multiline}
              <textarea
                id="tool-{tool.id}-{setting.key}"
                class="textarea textarea-bordered textarea-sm w-full focus:border-primary"
                rows="3"
                value={setting.value}
                on:input={(e) => updateToolTextSetting(setting.key, (e.target as HTMLTextAreaElement)?.value || '')}
                placeholder={setting.label}
              ></textarea>
            {:else}
              <input
                id="tool-{tool.id}-{setting.key}"
                type="text"
                class="input input-bordered input-sm w-full focus:border-primary"
                value={setting.value}
                on:input={(e) => updateToolTextSetting(setting.key, (e.target as HTMLInputElement)?.value || '')}
                placeholder={setting.label}
              />
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- FeatureInfo Fields UI -->
  {#if tool.name?.toLowerCase() === 'featureinfo'}
    <div class="space-y-3">
      <div class="flex items-center space-x-2">
        <div class="w-1 h-4 bg-accent rounded"></div>
        <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide flex items-center gap-2">
          FeatureInfo Fields
          <span class="normal-case">
            <HelpTooltip tip="Configureer velden die worden gebruikt voor het tonen van feature-informatie." />
          </span>
        </h5>
      </div>
      <div class="space-y-2 pl-3">
        {#if featureInfoFields.length === 0}
          <div class="text-sm text-gray-500">No fields added yet.</div>
        {/if}
        {#each featureInfoFields as fieldObj, idx}
          <div class="flex gap-2 mb-1 items-center">
            <input
              class="input input-bordered w-1/2"
              placeholder="Field name (e.g. image)"
              value={fieldObj.field}
              on:input={(e) => {
                const newFields = [...featureInfoFields];
                newFields[idx].field = (e.target as HTMLInputElement).value;
                updateFeatureInfoFields(newFields);
              }}
            />
            <select
              class="select select-bordered w-1/3"
              value={fieldObj.handler}
              on:change={(e) => {
                const newFields = [...featureInfoFields];
                newFields[idx].handler = (e.target as HTMLSelectElement).value;
                updateFeatureInfoFields(newFields);
              }}
            >
              <option value="image">Image</option>
              <option value="pdf">PDF</option>
              <option value="chart">Chart</option>
            </select>
            <button type="button" class="btn btn-xs btn-error" on:click={() => {
              const newFields = featureInfoFields.filter((_, i) => i !== idx);
              updateFeatureInfoFields(newFields);
            }}>Remove</button>
          </div>
        {/each}
        <button type="button" class="btn btn-xs btn-primary mt-1" on:click={() => {
          const newFields = [...featureInfoFields, { field: '', handler: 'image' }];
          updateFeatureInfoFields(newFields);
        }}>+ Add Field</button>
      </div>
    </div>
  {/if}

  <!-- LayerLibrary Connectors UI -->
  {#if tool.name?.toLowerCase() === 'layerlibrary'}
    {@const layerLibraryConnectors = getLayerLibraryConnectors()}
    <div class="mb-4">
      <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide flex items-center gap-2">
        Connectors
        <span class="normal-case">
          <HelpTooltip tip="Configureer data connectors voor de LayerLibrary tool." />
        </span>
      </h5>
      {#each layerLibraryConnectors as connector, idx (idx)}
        <div class="border rounded p-3 mb-2 space-y-2">
          <div class="flex justify-between items-center">
            <div class="flex-1">
              <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-type-${idx}`}>
                Type
                <span class="normal-case">
                  <HelpTooltip tip="Type van connector. Momenteel wordt voornamelijk 'ckan' ondersteund." />
                </span>
              </label>
              <select 
                id={`connector-type-${idx}`} 
                class="select select-bordered select-sm w-full" 
                value={connector.type || ''}
                on:change={(e) => {
                  const newConnectors = [...layerLibraryConnectors];
                  newConnectors[idx].type = (e.target as HTMLSelectElement).value;
                  updateLayerLibraryConnectors(newConnectors);
                }}
              >
                <option value="">Selecteer type</option>
                <option value="ckan">CKAN</option>
                <option value="geonetwork">geonetwork</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <button type="button" class="btn btn-xs btn-error ml-2" title="Remove Connector" on:click={() => {
              const connectors = layerLibraryConnectors.filter((_, i) => i !== idx);
              updateLayerLibraryConnectors(connectors);
            }}>Remove</button>
          </div>
          <!-- Add more connector fields as needed -->
        </div>
      {/each}
      <button type="button" class="btn btn-xs btn-primary mt-2" on:click={() => {
        const connectors = [...layerLibraryConnectors, {
          type: 'ckan',
          url: '',
          organizations: [],
          groups: [],
          packages: []
        }];
        updateLayerLibraryConnectors(connectors);
      }}>+ Add Connector</button>
    </div>
  {/if}
</div>
{/if}
