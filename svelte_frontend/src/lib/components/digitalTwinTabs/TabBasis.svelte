<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchDigitalTwin,
    fetchDigitalTwinViewer,
    updateDigitalTwinViewer,
    fetchTools,
    bulkModifyToolAssociations
  } from '$lib/api';
  import type { DigitalTwin, DigitalTwinViewerResponse } from '$lib/types/digitalTwin';
  import type { BulkToolOperation } from '$lib/types/digitalTwinAssociation';
  import type { Tool } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  export let digitalTwinId: string;

  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;

  let colorsOpen = false;
  let viewerData: DigitalTwinViewerResponse | null = null;
  let digitalTwinData: DigitalTwin | null = null;
  let error: string | null = null;

  // Local editable copies of fields
  let logo = '';
  let thumbnail = '';
  let startPosition = {
    x: 0,
    y: 0,
    z: 0,
    heading: 0,
    pitch: 0,
    duration: 0
  };
  let colors: Record<string, string> = {};
  let allTools: (Tool & { enabled: boolean; settings?: Record<string, any> })[] = [];
  let activeToolSettingsTab: number | null = null;

  // FeatureInfo fields state (for the featureinfo tool)
  let featureInfoFields: { field: string; handler: string }[] = [];

  // Tool setting tooltips lookup
  const toolSettingTooltips: Record<string, string> = {
    // LayerLibrary tool
    'useTags': "Optioneel: Als dit is ingesteld op 'true', is het mogelijk om datasets in de Bibliotheek te filteren op basis van hun tags.",

    // Info tool
    "title": "Titel van de digital twin.",
    "description": "Beschrijving van de digital twin.",

    // Help tool
    "showOnStart": "Toon het help tool bij het openen van de viewer.",
    "intro": "Introductie tekst voor het help tool, waarbij gebruik van html elementen mogelijk is.",

    // Geocoder tool
    "name": "Geocoder-tool, geplaatst in de rechterhoek van de header in plaats van de werkbalk, hiermee kan de gebruiker locaties opzoeken en er naartoe inzoomen.",

    // Flooding tool
    "scenariosBaseUrl": "Basis URL voor het scenario.",
    "breachUrl": "Basis URL voor de overstroming.",
    "roadsUrl": "Basis URL voor de wegen.",
    "floodedRoadsUrl": "Basis URL voor de overstroomde wegen.",

    // Config switcher tool
    "fullReload": "Of de volledige pagina opnieuw wordt geladen bij het wisselen van configuraties, wat de URL van de pagina zal veranderen. Indien false, worden alleen bepaalde componenten opnieuw geladen.",

  };

  onMount(async () => {
    try {
      digitalTwinData = await fetchDigitalTwin(digitalTwinId);
      viewerData = await fetchDigitalTwinViewer(digitalTwinId);

      // Initialize local copies with safe defaults
      logo = viewerData.content.logo ?? '';
      thumbnail = viewerData.content.thumbnail ?? '';
      startPosition = {
        x: viewerData.content.startPosition?.x ?? 0,
        y: viewerData.content.startPosition?.y ?? 0,
        z: viewerData.content.startPosition?.z ?? 0,
        heading: viewerData.content.startPosition?.heading ?? 0,
        pitch: viewerData.content.startPosition?.pitch ?? 0,
        duration: viewerData.content.startPosition?.duration ?? 0
      };
      colors = { ...viewerData.content.colors };

      // Fetch tools
      const toolsFromApi = await fetchTools();

      // Get enabled tool IDs from the viewer's tool_associations
      // if tool_associations is undefined, use empty array
      const enabledToolIds = new Set(
        (digitalTwinData?.tool_associations ?? []).map((t) => t.tool_id)
      );

      // Combine tools with enabled info and settings
      allTools = toolsFromApi.map((tool: Tool) => {
        const enabled = enabledToolIds.has(tool.id);
        // Get existing settings from tool association if available
        const existingAssociation = digitalTwinData?.tool_associations?.find(assoc => assoc.tool_id === tool.id);
        const existingSettings = existingAssociation?.content || {};
        
        return {
          ...tool,
          enabled,
          settings: enabled ? { 
            ...tool.content?.settings, // Default settings from tool definition
            ...existingSettings // Override with saved settings
          } : undefined
        };
      });

      // Sync featureInfoFields after allTools is initialized
      syncFeatureInfoFieldsFromTools();
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : String(e);
    }
  });

  // Helper to sync featureInfoFields from allTools (call on mount and when active tab changes)
  function syncFeatureInfoFieldsFromTools() {
    const featureInfoTool = allTools.find(t => t.name?.toLowerCase() === 'featureinfo');
    if (featureInfoTool && featureInfoTool.enabled) {
      if (Array.isArray(featureInfoTool.settings?.fields)) {
        featureInfoFields = featureInfoTool.settings.fields.map((f: any) => ({ field: f.field || '', handler: f.handler || 'image' }));
      } else {
        featureInfoFields = [];
      }
    } else {
      featureInfoFields = [];
    }
  }

  // Also call sync when activeToolSettingsTab changes (in case user switches tabs)
  $: if (activeToolSettingsTab !== null) {
    syncFeatureInfoFieldsFromTools();
  }

  // Helper to update allTools when user changes featureInfoFields
  function updateFeatureInfoFields(newFields: { field: string; handler: string }[]) {
    featureInfoFields = newFields;
    const featureInfoTool = allTools.find(t => t.name?.toLowerCase() === 'featureinfo');
    if (featureInfoTool && featureInfoTool.enabled) {
      featureInfoTool.settings = featureInfoTool.settings || {};
      featureInfoTool.settings.fields = featureInfoFields.map(f => ({ field: f.field, handler: f.handler }));
      allTools = allTools;
    }
  }

  // Reactive statement to calculate tools with settings
  $: toolsWithSettings = allTools.filter(tool => {
    if (!tool.enabled) return false;
    const booleanSettings = getConfigurableBooleanSettings(tool);
    const textSettings = getConfigurableTextSettings(tool);
    if (tool.name?.toLowerCase() === 'featureinfo') return true;
    return booleanSettings.length > 0 || textSettings.length > 0;
  });

  // Reactive statement to initialize active tab
  $: {
    if (activeToolSettingsTab === null && toolsWithSettings.length > 0) {
      activeToolSettingsTab = toolsWithSettings[0].id;
    }
    
    // Reset if current active tab is no longer available
    if (activeToolSettingsTab !== null && !toolsWithSettings.some(tool => tool.id === activeToolSettingsTab)) {
      activeToolSettingsTab = toolsWithSettings.length > 0 ? toolsWithSettings[0].id : null;
    }
  }

  function toggleTool(toolId: number) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool) {
      tool.enabled = !tool.enabled;
      
      // Initialize settings if tool is being enabled and has default settings
      if (tool.enabled && tool.content?.settings) {
        tool.settings = { ...tool.content.settings };
      } else if (!tool.enabled) {
        // Clear settings when tool is disabled
        tool.settings = undefined;
      }
      
      // Trigger reactivity
      allTools = allTools;
    }
  }

  function toggleToolSetting(toolId: number, settingKey: string) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = !tool.settings[settingKey];
      // Trigger reactivity
      allTools = allTools;
    }
  }

  function updateToolTextSetting(toolId: number, settingKey: string, value: string) {
    const tool = allTools.find((t) => t.id === toolId);
    if (tool && tool.settings) {
      tool.settings[settingKey] = value;
      // Trigger reactivity
      allTools = allTools;
    }
  }

  // Helper function to get configurable boolean settings for a tool
  function getConfigurableBooleanSettings(tool: Tool) {
    if (!tool.content?.settings) return [];
    const currentTool = allTools.find(t => t.id === tool.id);
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'boolean')
      .map(([key, value]) => ({
        key,
        value: currentTool?.settings?.[key] ?? value,
        label: key // You may want to map key to a user-friendly label
      }));
  }

  // Helper function to get configurable text settings for a tool
  function getConfigurableTextSettings(tool: Tool) {
    if (!tool.content?.settings) return [];
    const currentTool = allTools.find(t => t.id === tool.id);
    return Object.entries(tool.content.settings)
      .filter(([_, value]) => typeof value === 'string')
      .map(([key, value]) => ({
        key,
        value: currentTool?.settings?.[key] ?? value,
        label: key, // Map to user-friendly label if needed
        multiline: key === 'description' // Or use a config for which fields are multiline
      }));
  }

  // Computed property for LayerLibrary connectors (getter/setter)
  function getLayerLibraryConnectors(tool: Tool & { enabled: boolean; settings?: Record<string, any> }): any[] {
    // Defensive: always return array
    return tool.settings?.connectors ?? [];
  }
  function setLayerLibraryConnectors(tool: Tool & { enabled: boolean; settings?: Record<string, any> }, newConnectors: any[]): void {
    if (tool.settings) {
      // Deep clone to ensure Svelte reactivity
      tool.settings.connectors = JSON.parse(JSON.stringify(newConnectors));
      allTools = [...allTools];
    }
  }

  async function handleSubmit() {
    try {
      // Get current enabled tools from state
      const currentlyEnabled = new Set(allTools.filter((t) => t.enabled).map((t) => t.id));

      // Get originally enabled tool IDs from viewer data
      const originallyEnabled = new Set(
        (digitalTwinData?.tool_associations ?? []).map((t) => t.tool_id)
      );

      // Tools to add and delete
      const toolsToAdd = [...currentlyEnabled].filter((id) => !originallyEnabled.has(id));
      const toolsToRemove = [...originallyEnabled].filter((id) => !currentlyEnabled.has(id));

      // Prepare operations for bulk API
      const operations: BulkToolOperation[] = [
        ...toolsToAdd.map((id) => {
          const tool = allTools.find(t => t.id === id);
          return {
            tool_id: id,
            action: 'create' as const,
            content: tool?.settings || {}
          };
        }),
        ...toolsToRemove.map((id) => ({ 
          tool_id: id, 
          action: 'delete' as const 
        }))
      ];

      // Add update operations for tools with changed settings
      for (const tool of allTools.filter(t => t.enabled && originallyEnabled.has(t.id))) {
        const originalAssociation = digitalTwinData?.tool_associations?.find(assoc => assoc.tool_id === tool.id);
        const originalSettings = originalAssociation?.content || {};
        
        // Check if settings have changed
        if (JSON.stringify(tool.settings) !== JSON.stringify(originalSettings)) {
          operations.push({
            tool_id: tool.id,
            action: 'update',
            content: tool.settings || {}
          });
        }
      }

      // Call bulk API only if there are operations
      if (operations.length > 0) {
        await bulkModifyToolAssociations(digitalTwinId, operations);
      }

      // Update viewer content
      await updateDigitalTwinViewer(digitalTwinId, {
        logo,
        thumbnail,
        startPosition,
        colors
      });

      successBanner?.show();
    } catch (err) {
      console.error(err);
      errorBanner?.show;
    }
  }
</script>

<!-- AlertBanners that are only visable after the submit button is pressed -->
<AlertBanner bind:this={successBanner} type="success" message="Digital Twin Viewer bijgewerkt!" />
<AlertBanner bind:this={errorBanner} type="error" message="Fout bij het opslaan!" />

{#if error}
  <div class="alert alert-error">{error}</div>
{:else if !viewerData}
  <div>Loading...</div>
{:else}
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Basis Instellingen</h2>
    <p class="text-base-content/70">Basis configuratie voor deze digital twin.</p>

    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body space-y-4">
        <!-- Logo -->
        <div>
          <label for="logo-url" class="font-medium flex items-center gap-2">
            Logo URL
            <HelpTooltip tip="URL van het logo dat wordt weergegeven in de viewer." />
          </label>
          <input id="logo-url" type="text" bind:value={logo} class="input input-bordered w-full" />
        </div>

        <!-- Thumbnail -->
        <div>
          <label for="thumbnail-url" class="font-medium flex items-center gap-2">
            Thumbnail URL
            <HelpTooltip tip="URL van de thumbnail-afbeelding voor deze digital twin." />
          </label>
          <input
            id="thumbnail-url"
            type="text"
            bind:value={thumbnail}
            class="input input-bordered w-full"
          />
        </div>

        <!-- Start Position in 3 columns (defined by grid-cols-3)-->
        <fieldset>
          <legend class="font-semibold mb-2">Start positie</legend>
          
          <!-- Position Selector Button -->
          <div class="mb-4">
            <PositionSelector 
              title="Selecteer start positie"
              buttonText="Selecteer start positie op kaart"
              initialPosition={startPosition}
              on:coordinatesSelected={(e) => {
                startPosition = e.detail;
              }}
            />
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="start-x" class="font-medium flex items-center gap-2">
                X
                <HelpTooltip tip="X-coördinaat van de startpositie." />
              </label>
              <input
                id="start-x"
                type="number"
                step="any"
                bind:value={startPosition.x}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-y" class="font-medium flex items-center gap-2">
                Y
                <HelpTooltip tip="Y-coördinaat van de startpositie." />
              </label>
              <input
                id="start-y"
                type="number"
                step="any"
                bind:value={startPosition.y}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-z" class="font-medium flex items-center gap-2">
                Z
                <HelpTooltip tip="Z-coördinaat (hoogte) van de startpositie." />
              </label>
              <input
                id="start-z"
                type="number"
                step="any"
                bind:value={startPosition.z}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-heading" class="font-medium flex items-center gap-2">
                Heading
                <HelpTooltip tip="Kijkrichting (in graden) van de camera bij het starten." />
              </label>
              <input
                id="start-heading"
                type="number"
                step="any"
                bind:value={startPosition.heading}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-pitch" class="font-medium flex items-center gap-2">
                Pitch
                <HelpTooltip tip="Kantelhoek van de camera bij het starten." />
              </label>
              <input
                id="start-pitch"
                type="number"
                step="any"
                bind:value={startPosition.pitch}
                class="input input-bordered w-full"
              />
            </div>

            <div>
              <label for="start-duration" class="font-medium flex items-center gap-2">
                Duration
                <HelpTooltip tip="Duur van de overgang naar de startpositie (in seconden)." />
              </label>
              <input
                id="start-duration"
                type="number"
                step="any"
                bind:value={startPosition.duration}
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </fieldset>

        <!-- Tools checkboxes list in 3 column grid (defined by class grid-cols-3) -->
        <fieldset>
          <legend class="mb-2 font-semibold">Tools
            <HelpTooltip tip="Selecteer de tools die je wilt gebruiken voor deze digital twin." />
          </legend>
          <div class="space-y-3">
            <div
              class="grid max-h-48 grid-cols-3 gap-2 overflow-auto rounded border border-gray-300 p-2"
            >
              {#each allTools as tool (tool.id)}
                <label class="flex cursor-pointer items-center space-x-2 select-none">
                  <input
                    type="checkbox"
                    checked={tool.enabled}
                    on:change={() => toggleTool(tool.id)}
                    class="checkbox checkbox-primary"
                  />
                  <span>{tool.name}</span>
                </label>
              {/each}
            </div>
            
            <!-- Tool Settings -->
            {#if toolsWithSettings.length > 0}
              <div class="bg-base-50 rounded-lg">
                <h3 class="font-semibold text-base">Tool Settings
                  <HelpTooltip tip="Tool instellingen voor de geselecteerde tool." />
                </h3>
                <!-- Tool Settings Tabs -->
                <div class="tabs tabs-border">
                  {#each toolsWithSettings as tool, index (tool.id)}
                    {@const configurableBooleanSettings = getConfigurableBooleanSettings(tool)}
                    {@const configurableTextSettings = getConfigurableTextSettings(tool)}
                    <input 
                      type="radio" 
                      name="tool_settings_tabs" 
                      class="tab" 
                      aria-label={tool.name}
                      checked={activeToolSettingsTab === tool.id}
                      on:change={() => activeToolSettingsTab = tool.id}
                    />
                    <div class="tab-content border-base-300 bg-base-100 p-6">
                      <div class="space-y-4">
                        <!-- Boolean Settings -->
                        {#if configurableBooleanSettings.length > 0}
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
                                    on:change={() => toggleToolSetting(tool.id, setting.key)}
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
                        {#if configurableTextSettings.length > 0}
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
                                      on:change={(e) => updateToolTextSetting(tool.id, setting.key, (e.target as HTMLSelectElement)?.value || '')}
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
                                      on:input={(e) => updateToolTextSetting(tool.id, setting.key, (e.target as HTMLTextAreaElement)?.value || '')}
                                      placeholder={setting.label}
                                    ></textarea>
                                  {:else}
                                    <input
                                      id="tool-{tool.id}-{setting.key}"
                                      type="text"
                                      class="input input-bordered input-sm w-full focus:border-primary"
                                      value={setting.value}
                                      on:input={(e) => updateToolTextSetting(tool.id, setting.key, (e.target as HTMLInputElement)?.value || '')}
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
                                  <HelpTooltip tip="Configureer velden die worden gebruikt voor het tonen van feature-informatie. Specificeer het veldnaam en het bijbehorende handler type (image, PDF, of chart)." />
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
                          <div class="mb-4">
                            <h5 class="font-semibold text-sm text-base-content uppercase tracking-wide flex items-center gap-2">
                              Connectors
                              <span class="normal-case">
                                <HelpTooltip tip="Configureer data connectors voor de LayerLibrary tool. Elke connector definieert een bron van datasets met bijbehorende organisaties, groepen en pakketten." />
                              </span>
                            </h5>
                            {#each getLayerLibraryConnectors(tool) as connector, idx (idx)}
                              <div class="border rounded p-3 mb-2 space-y-2">
                                <div class="flex justify-between items-center">
                                  <div class="flex-1">
                                    <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-type-${idx}`}>
                                      Type
                                      <span class="normal-case">
                                        <HelpTooltip tip="Type van connector. Momenteel wordt voornamelijk 'ckan' ondersteund voor CKAN data catalogi." />
                                      </span>
                                    </label>
                                    <select 
                                      id={`connector-type-${idx}`} 
                                      class="select select-bordered select-sm w-full" 
                                      bind:value={connector.type}
                                      on:change={(e) => {
                                        const connectors = [...getLayerLibraryConnectors(tool)];
                                        connectors[idx].type = (e.target as HTMLSelectElement).value;
                                        setLayerLibraryConnectors(tool, connectors);
                                      }}
                                    >
                                      <option value="">Selecteer type</option>
                                      <option value="ckan">CKAN</option>
                                      <option value="geonetwork">geonetwork</option>
                                      <option value="custom">Custom</option>
                                    </select>
                                    {#if connector.type === 'custom'}
                                      <input
                                        type="text"
                                        class="input input-bordered input-sm w-full mt-2"
                                        placeholder="Voer custom connector type in..."
                                        value={connector.customType || ''}
                                        on:input={(e) => {
                                          const connectors = [...getLayerLibraryConnectors(tool)];
                                          connectors[idx].customType = (e.target as HTMLInputElement).value;
                                          setLayerLibraryConnectors(tool, connectors);
                                        }}
                                      />
                                    {/if}
                                  </div>
                                  <button type="button" class="btn btn-xs btn-error ml-2" title="Remove Connector" on:click={() => {
                                    const connectors = getLayerLibraryConnectors(tool).filter((_, i) => i !== idx);
                                    setLayerLibraryConnectors(tool, connectors);
                                  }}>Remove</button>
                                </div>
                                <div>
                                  <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-url-${idx}`}>
                                    URL
                                    <span class="normal-case">
                                      <HelpTooltip tip="De basis URL van de data connector service." />
                                    </span>
                                  </label>
                                  <input id={`connector-url-${idx}`} type="text" class="input input-bordered input-sm w-full" bind:value={connector.url}
                                    on:input={(e) => {
                                      const connectors = [...getLayerLibraryConnectors(tool)];
                                      connectors[idx].url = (e.target as HTMLInputElement).value;
                                      setLayerLibraryConnectors(tool, connectors);
                                    }} />
                                </div>
                                <div>
                                  <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-orgs-${idx}`}>
                                    Organizations (comma separated)
                                    <span class="normal-case">
                                      <HelpTooltip tip="Lijst van organisaties waarvan datasets beschikbaar zijn via deze connector. Gebruik komma's om meerdere organisaties te scheiden." />
                                    </span>
                                  </label>
                                  <input id={`connector-orgs-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.organizations) ? connector.organizations.join(', ') : connector.organizations}
                                    on:input={(e) => {
                                      const connectors = [...getLayerLibraryConnectors(tool)];
                                      connectors[idx].organizations = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                      setLayerLibraryConnectors(tool, connectors);
                                    }} />
                                </div>
                                <div>
                                  <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-groups-${idx}`}>
                                    Groups (comma separated)
                                    <span class="normal-case">
                                      <HelpTooltip tip="Lijst van groepen waarvan datasets beschikbaar zijn via deze connector. Gebruik komma's om meerdere groepen te scheiden." />
                                    </span>
                                  </label>
                                  <input id={`connector-groups-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.groups) ? connector.groups.join(', ') : connector.groups}
                                    on:input={(e) => {
                                      const connectors = [...getLayerLibraryConnectors(tool)];
                                      connectors[idx].groups = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                      setLayerLibraryConnectors(tool, connectors);
                                    }} />
                                </div>
                                <div>
                                  <label class="text-xs font-semibold mb-1 flex items-center gap-2" for={`connector-packages-${idx}`}>
                                    Packages (comma separated)
                                    <span class="normal-case">
                                      <HelpTooltip tip="Lijst van data-pakketten die beschikbaar zijn via deze connector. Gebruik komma's om meerdere pakketten te scheiden." />
                                    </span>
                                  </label>
                                  <input id={`connector-packages-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.packages) ? connector.packages.join(', ') : connector.packages}
                                    on:input={(e) => {
                                      const connectors = [...getLayerLibraryConnectors(tool)];
                                      connectors[idx].packages = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                      setLayerLibraryConnectors(tool, connectors);
                                    }} />
                                </div>
                                <div>
                                  <span class="text-xs font-semibold mb-1 flex items-center gap-2">
                                    Special Resources
                                    <span class="normal-case">
                                      <HelpTooltip tip="Speciale resource configuraties voor achtergrond lagen en automatisch toe te voegen/verwijderen lagen." />
                                    </span>
                                  </span>
                                  <div class="space-y-1 ml-5">
                                    <label class="text-xs flex items-center gap-2" for={`connector-bg-${idx}`}>
                                      Background Layers (comma separated)
                                      <span class="normal-case">
                                        <HelpTooltip tip="Lagen die automatisch als achtergrond worden geladen wanneer deze connector wordt gebruikt." />
                                      </span>
                                    </label>
                                    <input id={`connector-bg-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.specialResources?.backgroundLayers) ? connector.specialResources.backgroundLayers.join(', ') : connector.specialResources?.backgroundLayers}
                                      on:input={(e) => {
                                        const connectors = [...getLayerLibraryConnectors(tool)];
                                        connectors[idx].specialResources.backgroundLayers = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                        setLayerLibraryConnectors(tool, connectors);
                                      }} />
                                    <label class="text-xs flex items-center gap-2" for={`connector-on-${idx}`}>
                                      Layers Added On (comma separated)
                                      <span class="normal-case">
                                        <HelpTooltip tip="Lagen die automatisch worden ingeschakeld wanneer deze connector wordt geactiveerd." />
                                      </span>
                                    </label>
                                    <input id={`connector-on-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.specialResources?.layersAddedOn) ? connector.specialResources.layersAddedOn.join(', ') : connector.specialResources?.layersAddedOn}
                                      on:input={(e) => {
                                        const connectors = [...getLayerLibraryConnectors(tool)];
                                        connectors[idx].specialResources.layersAddedOn = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                        setLayerLibraryConnectors(tool, connectors);
                                      }} />
                                    <label class="text-xs flex items-center gap-2" for={`connector-off-${idx}`}>
                                      Layers Added Off (comma separated)
                                      <span class="normal-case">
                                        <HelpTooltip tip="Lagen die automatisch worden uitgeschakeld wanneer deze connector wordt geactiveerd." />
                                      </span>
                                    </label>
                                    <input id={`connector-off-${idx}`} type="text" class="input input-bordered input-sm w-full" value={Array.isArray(connector.specialResources?.layersAddedOff) ? connector.specialResources.layersAddedOff.join(', ') : connector.specialResources?.layersAddedOff}
                                      on:input={(e) => {
                                        const connectors = [...getLayerLibraryConnectors(tool)];
                                        connectors[idx].specialResources.layersAddedOff = (e.target as HTMLInputElement).value.split(',').map(s => s.trim());
                                        setLayerLibraryConnectors(tool, connectors);
                                      }} />
                                  </div>
                                </div>
                              </div>
                            {/each}
                            <button type="button" class="btn btn-xs btn-primary mt-2" on:click={() => {
                              const connectors = [...getLayerLibraryConnectors(tool), {
                                type: 'ckan',
                                customType: '',
                                url: '',
                                organizations: [],
                                groups: [],
                                packages: [],
                                specialResources: {
                                  backgroundLayers: [],
                                  layersAddedOn: [],
                                  layersAddedOff: []
                                }
                              }];
                              setLayerLibraryConnectors(tool, connectors);
                            }}>+ Add Connector</button>
                          </div>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </fieldset>

        <!-- Colors with color pickers in 5 columns grid (defined by class grid-cols-5) -->
        <fieldset>
          <button
            type="button"
            class="m-0 flex w-full cursor-pointer items-center space-x-2 border-0 bg-transparent p-0 text-left font-semibold select-none"
            on:click={() => (colorsOpen = !colorsOpen)}
            aria-expanded={colorsOpen}
          >
            {#if colorsOpen}
              <img src="/icons/chevron-down.svg" alt="Open" class="h-5 w-5" />
            {:else}
              <img src="/icons/chevron-right.svg" alt="Closed" class="h-5 w-5" />
            {/if}
            <span>Colors
              <HelpTooltip tip="Kleurinstellingen voor de digital twin." />
            </span>
          </button>

          {#if colorsOpen}
            <div class="mt-2 grid grid-cols-5 gap-4">
              {#each Object.entries(colors) as [key, value]}
                <div>
                  <label for={'color-' + key} class="truncate font-medium flex items-center gap-2">
                    {key}
                  </label>
                  <input
                    id={'color-' + key}
                    type="color"
                    bind:value={colors[key]}
                    class="h-8 w-12 rounded border border-gray-300 p-0"
                  />
                  <input
                    type="text"
                    bind:value={colors[key]}
                    class="input input-bordered mt-1 w-full"
                  />
                </div>
              {/each}
            </div>
          {/if}
        </fieldset>

        <button on:click={handleSubmit} class="btn btn-primary mt-4">Opslaan</button>
      </div>
    </div>
  </div>
{/if}
