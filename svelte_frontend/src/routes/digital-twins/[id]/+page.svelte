<script lang="ts">
  import TabOmschrijving from '$lib/components/digitalTwinTabs/TabOmschrijving.svelte';
  import TabBasis from '$lib/components/digitalTwinTabs/TabBasis.svelte';
  import TabOndergrond from '$lib/components/digitalTwinTabs/TabOndergrond.svelte';
  import TabFeatureLagen from '$lib/components/digitalTwinTabs/TabFeatureLagen.svelte';
  import TabBookmarks from '$lib/components/digitalTwinTabs/TabBookmarks.svelte';
  import TabStories from '$lib/components/digitalTwinTabs/TabStories.svelte';
  import TabProjects from '$lib/components/digitalTwinTabs/TabProjects.svelte';
  import TabTerrainProvider from '$lib/components/digitalTwinTabs/TabTerrainProvider.svelte';
  import UnsavedChangesModal from '$lib/components/modals/UnsavedChangesModal.svelte';
  import { onMount, onDestroy } from 'svelte';
  import { beforeNavigate, goto } from '$app/navigation';
  import { browser } from '$app/environment';

  import { digitalTwinExport } from '$lib/api';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let tabs = [
    { label: 'Omschrijving', component: TabOmschrijving },
    { label: 'Basis', component: TabBasis },
    { label: 'Ondergrond', component: TabOndergrond },
    { label: 'FeatureLagen', component: TabFeatureLagen },
    { label: 'TerrainProviders', component: TabTerrainProvider },
    { label: 'Bookmarks', component: TabBookmarks },
    { label: 'Stories', component: TabStories },
    { label: 'Projects', component: TabProjects }
  ];

  let selectedIndex = $state(0);
  let pendingTabIndex = $state<number | null>(null);
  let showUnsavedChangesModal = $state(false);
  
  // Track changes in each tab component - make this reactive
  let tabRefs = $state<Array<any>>([]);
  
  // Store navigation attempt for modal handling - needs to be reactive
  let pendingNavigation = $state<{ type: 'internal' | 'external'; url?: string; navigation?: any } | null>(null);
  
  // Function to get user-friendly destination name from URL
  function getDestinationName(url: string): string {
    if (!url) return 'een andere pagina';
    
    // Handle relative and absolute URLs safely for SSR
    let path: string;
    if (url.includes('://')) {
      // For absolute URLs, extract pathname safely
      try {
        // Only use URL constructor in browser environment
        if (browser) {
          path = new URL(url).pathname;
        } else {
          // Fallback for SSR - simple string parsing
          const urlParts = url.split('/');
          const pathIndex = urlParts.indexOf('', 3); // Find the first empty string after protocol
          path = pathIndex >= 0 ? '/' + urlParts.slice(pathIndex + 1).join('/') : url;
        }
      } catch {
        // Fallback if URL parsing fails
        path = url;
      }
    } else {
      path = url;
    }
    
    // Map common paths to user-friendly names
    const pathMap: Record<string, string> = {
      '/': 'de startpagina',
      '/digital-twins': 'Digital Twins overzicht',
      '/tools': 'Tools overzicht',
      '/projects': 'Projecten overzicht',
      '/users': 'Gebruikers overzicht',
      '/settings': 'Instellingen',
      '/help': 'Help pagina'
    };
    
    // Check for exact match
    if (pathMap[path]) {
      return pathMap[path];
    }
    
    // Check for partial matches
    if (path.startsWith('/digital-twins/')) {
      return 'een andere Digital Twin';
    }
    if (path.startsWith('/tools/')) {
      return 'een tool';
    }
    if (path.startsWith('/projects/')) {
      return 'een project';
    }
    
    // Default fallback
    return `"${path}"`;
  }
  
  // Check if ANY tab has unsaved changes
  function anyTabHasChanges(): boolean {
    for (let i = 0; i < tabRefs.length; i++) {
      const tabRef = tabRefs[i];
      if (!tabRef) continue;
      
      // Try the exported getHasChanges method
      if (typeof tabRef.getHasChanges === 'function') {
        if (tabRef.getHasChanges() === true) {
          return true;
        }
      }
      // Fallback methods
      else if (typeof tabRef.hasChanges !== 'undefined' && tabRef.hasChanges === true) {
        return true;
      }
      else if (tabRef.$state && typeof tabRef.$state.hasChanges !== 'undefined' && tabRef.$state.hasChanges === true) {
        return true;
      }
    }
    return false;
  }
  
  // Function to check if current tab has unsaved changes
  function currentTabHasChanges(): boolean {
    const currentTabRef = tabRefs[selectedIndex];
    
    if (!currentTabRef) {
      return false;
    }
    
    // Try the new exported getHasChanges method
    if (typeof currentTabRef.getHasChanges === 'function') {
      const hasChanges = currentTabRef.getHasChanges();
      return hasChanges === true;
    }
    
    // Try different ways to access hasChanges
    let hasChanges = false;
    
    // Method 1: Direct property access
    if (typeof currentTabRef.hasChanges !== 'undefined') {
      hasChanges = currentTabRef.hasChanges;
    }
    // Method 2: Check if it's a getter
    else if (currentTabRef.$state && typeof currentTabRef.$state.hasChanges !== 'undefined') {
      hasChanges = currentTabRef.$state.hasChanges;
    }
    
    return hasChanges === true;
  }
  
  // Function to save changes in current tab
  async function saveCurrentTabChanges(): Promise<boolean> {
    const currentTabRef = tabRefs[selectedIndex];
    if (!currentTabRef) return true;
    
    try {
      // Try the new exported saveTabChanges method
      if (typeof currentTabRef.saveTabChanges === 'function') {
        console.log('Calling saveTabChanges method');
        await currentTabRef.saveTabChanges();
        return true;
      }
      // Try to call saveChanges method if it exists
      else if (typeof currentTabRef.saveChanges === 'function') {
        console.log('Calling saveChanges method');
        await currentTabRef.saveChanges();
        return true;
      }
      // For TabOmschrijving, try handleSubmit
      else if (typeof currentTabRef.handleSubmit === 'function') {
        console.log('Calling handleSubmit method');
        // Create a fake event for handleSubmit
        const fakeEvent = new Event('submit');
        await currentTabRef.handleSubmit(fakeEvent);
        return true;
      }
      console.log('No save method found');
      return true;
    } catch (error) {
      console.error('Failed to save tab changes:', error);
      return false;
    }
  }
  
  // Handle tab change with unsaved changes check
  function handleTabChange(targetIndex: number) {
    // If same tab, do nothing
    if (targetIndex === selectedIndex) return;
    
    // Check if current tab has unsaved changes
    const hasChanges = currentTabHasChanges();
    
    if (hasChanges) {
      pendingTabIndex = targetIndex;
      showUnsavedChangesModal = true;
      return;
    }
    
    // No unsaved changes, switch directly
    selectedIndex = targetIndex;
  }
  
  // Handle save and continue from modal
  async function handleSaveAndContinue() {
    if (pendingTabIndex === null && !pendingNavigation) return;
    
    try {
      // If it's a tab change, save current tab
      if (pendingTabIndex !== null) {
        const targetTab = pendingTabIndex;
        const saveSuccess = await saveCurrentTabChanges();
        
        if (saveSuccess) {
          // Add a small delay to ensure save is completed
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Switch to the new tab
          selectedIndex = targetTab;
          
          // Update the radio button to reflect the new selection
          setTimeout(() => {
            updateRadioSelection();
          }, 50);
        } else {
          console.error('Save failed, staying on current tab');
          return;
        }
      }
      // If it's navigation, save all tabs with changes
      else if (pendingNavigation) {
        const savePromises = [];
        
        // Save all tabs that have changes
        for (let i = 0; i < tabRefs.length; i++) {
          const tabRef = tabRefs[i];
          if (!tabRef) continue;
          
          // Check if this tab has changes and can be saved
          if (typeof tabRef.getHasChanges === 'function' && tabRef.getHasChanges() === true) {
            if (typeof tabRef.saveTabChanges === 'function') {
              savePromises.push(tabRef.saveTabChanges());
            }
          }
        }
        
        // Wait for all saves to complete
        const saveResults = await Promise.all(savePromises);
        
        // Check if all saves were successful
        if (saveResults.every(result => result === true)) {
          // All saves successful, proceed with navigation or export
          if (pendingNavigation.type === 'internal' && pendingNavigation.navigation) {
            const nav = pendingNavigation.navigation;
            
            // Check if this is an export action (downloadUrl)
            if (nav.to === downloadUrl || pendingNavigation.url === downloadUrl) {
              // Clear modal state and trigger download
              pendingNavigation = null;
              showUnsavedChangesModal = false;
              
              // Trigger the download after save
              const link = document.createElement('a');
              link.href = downloadUrl;
              link.download = '';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              return;
            } else {
              // Regular navigation
              // Clear pending state first
              pendingNavigation = null;
              showUnsavedChangesModal = false;
              
              // Use SvelteKit's proper navigation - much faster than window.location.href
              goto(nav.to?.url?.href || nav.to);
              return;
            }
          } else if (pendingNavigation.type === 'external') {
            // For external navigation, the browser will handle it
            // We just need to clear the beforeunload prevention
            window.removeEventListener('beforeunload', handleBeforeUnload);
            // Trigger a page reload or let the browser continue its action
            // (this case is mainly for the browser's built-in confirmation)
          }
        } else {
          console.error('Some saves failed, staying on page');
          return;
        }
      }
    } catch (error) {
      console.error('Error during save and continue:', error);
      return;
    }
    
    // Clear pending states
    pendingTabIndex = null;
    pendingNavigation = null;
    showUnsavedChangesModal = false;
  }
  
  // Handle continue without saving from modal
  function handleContinueWithoutSaving() {
    if (pendingTabIndex === null && !pendingNavigation) return;
    
    // If it's a tab change
    if (pendingTabIndex !== null) {
      const targetTab = pendingTabIndex;
      
      // Reset changes in current tab
      const currentTabRef = tabRefs[selectedIndex];
      if (currentTabRef) {
        // Try the new exported resetTabChanges method
        if (typeof currentTabRef.resetTabChanges === 'function') {
          currentTabRef.resetTabChanges();
        }
        // Try original resetChanges method
        else if (typeof currentTabRef.resetChanges === 'function') {
          currentTabRef.resetChanges();
        }
      }
      
      selectedIndex = targetTab;
      // Update the radio button to reflect the new selection
      updateRadioSelection();
    }
    // If it's navigation
    else if (pendingNavigation) {
      // Reset changes in all tabs
      for (let i = 0; i < tabRefs.length; i++) {
        const tabRef = tabRefs[i];
        if (!tabRef) continue;
        
        if (typeof tabRef.resetTabChanges === 'function') {
          tabRef.resetTabChanges();
        } else if (typeof tabRef.resetChanges === 'function') {
          tabRef.resetChanges();
        }
      }
      
      // Proceed with navigation or export
      if (pendingNavigation.type === 'internal' && pendingNavigation.navigation) {
        const nav = pendingNavigation.navigation;
        
        // Check if this is an export action
        if (nav.to === downloadUrl || pendingNavigation.url === downloadUrl) {
          // Clear modal state and trigger download without saving
          pendingNavigation = null;
          showUnsavedChangesModal = false;
          
          // Trigger the download with current (unsaved) state
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.download = '';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          return;
        } else {
          // Regular navigation
          // Clear state before navigation
          pendingNavigation = null;
          showUnsavedChangesModal = false;
          
          // Use SvelteKit's proper navigation
          goto(nav.to?.url?.href || nav.to);
          return;
        }
      } else if (pendingNavigation.type === 'external') {
        // Remove the beforeunload listener and let browser navigate
        window.removeEventListener('beforeunload', handleBeforeUnload);
        // For external navigation, we can't really "continue" it programmatically
        // The user will need to try their action again
      }
    }
    
    // Clear pending states
    pendingTabIndex = null;
    pendingNavigation = null;
    showUnsavedChangesModal = false;
  }
  
  // Handle cancel from modal
  function handleCancel() {
    // Reset pendingTabIndex without changing current tab
    pendingTabIndex = null;
    // Ensure the current radio button stays selected
    updateRadioSelection();
  }
  
  // Helper function to update radio button selection
  function updateRadioSelection() {
    // Force update of radio buttons to reflect current selectedIndex
    const radios = document.querySelectorAll('input[name="main_tabs"]');
    radios.forEach((radio, index) => {
      (radio as HTMLInputElement).checked = index === selectedIndex;
    });
  }
  
  // Intercept SvelteKit navigation (internal navigation)
  beforeNavigate((navigation) => {
    // Only intercept if we have unsaved changes and this is not the initial page load
    // Also ensure we're in the browser environment
    if (browser && currentTabHasChanges() && navigation.from) {
      // Cancel the navigation
      navigation.cancel();
      
      // Store the navigation for later
      pendingNavigation = {
        type: 'internal',
        navigation: navigation
      };
      
      // Show the modal
      showUnsavedChangesModal = true;
      return;
    }
  });

  // Intercept browser navigation (external links, back/forward, address bar, etc.)
  function handleBeforeUnload(event: BeforeUnloadEvent) {
    // Only check current tab for performance
    if (currentTabHasChanges()) {
      // Standard way to show browser confirmation dialog
      event.preventDefault();
      event.returnValue = ''; // Some browsers require this
      
      // Store this as external navigation
      pendingNavigation = {
        type: 'external'
      };
      
      return ''; // Legacy browsers
    }
  }

  // Set up event listeners
  onMount(() => {
    if (browser) {
      window.addEventListener('beforeunload', handleBeforeUnload);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  });

  const downloadUrl = $derived(data.id ? digitalTwinExport(data.id) : '#');

  // Handle export button click with unsaved changes check
  function handleExportClick(event: Event) {
    // Check if there are any unsaved changes
    if (anyTabHasChanges()) {
      // Prevent the default download
      event.preventDefault();
      
      // Store export action for modal handling
      pendingNavigation = {
        type: 'internal',
        url: downloadUrl,
        navigation: { to: downloadUrl }
      };
      
      // Show modal asking user what to do
      showUnsavedChangesModal = true;
      return false;
    }
    
    // No changes, allow normal export
    return true;
  }
</script>

<svelte:head>
  <title>Digital Twin Configuratie - Digital Twins Manager</title>
</svelte:head>

{#if data.error}
  <div class="alert alert-error">
    <div>
      <h3 class="font-bold">Fout bij laden</h3>
      <div class="text-sm">{data.error}</div>
    </div>
  </div>
{:else if !data.digitalTwin}
  <div class="flex items-center justify-center p-8">
    <span class="loading loading-spinner loading-lg"></span>
    <span class="ml-3">Laden...</span>
  </div>
{:else}
<div class="space-y-6">
  <div class="flex items-center gap-4">
    <a href="/digital-twins" class="btn btn-ghost btn-sm">
      <img src="/icons/arrow-left.svg" alt="Ga terug" class="h-4 w-4" />
      Terug
    </a>
    <div>
      <h1 class="text-3xl font-bold">Digital Twin Configuratie</h1>
      <p class="text-base-content/70 mt-2">
        {data.digitalTwin?.title || `Digital twin ID: ${data.id || 'Onbekend'}`}
      </p>
    </div>
    {#if downloadUrl && downloadUrl !== '#'}
    <a
      href={downloadUrl}
      class="btn btn-primary flex items-center gap-2 ml-auto"
      download
      onclick={handleExportClick}
    >
      <img src="/icons/download.svg" alt="Download" class="w-5 h-5" />
      Download export
    </a>
    {/if}
  </div>

  <!-- Tab headers -->
  <div class="tabs tabs-border mb-4" role="tablist">
    {#each tabs as tab, i}
      <input
        type="radio"
        name="main_tabs"
        class="tab"
        aria-label={tab.label}
        checked={selectedIndex === i}
        onchange={(e) => {
          // Prevent default radio button behavior if we need to show modal
          const target = e.target as HTMLInputElement;
          if (target.checked && i !== selectedIndex) {
            const hasChanges = currentTabHasChanges();
            if (hasChanges) {
              // Prevent the radio button change
              e.preventDefault();
              target.checked = false;
              // Find the current tab radio and keep it checked
              const currentRadio = target.parentElement?.parentElement?.children[selectedIndex]?.querySelector('input[type="radio"]') as HTMLInputElement;
              if (currentRadio) {
                currentRadio.checked = true;
              }
              // Show modal
              pendingTabIndex = i;
              showUnsavedChangesModal = true;
              return;
            }
            // No changes, allow normal tab switch
            selectedIndex = i;
          }
        }}
      />
      <div class="tab-content border-base-300 bg-base-100 p-6 shadow-xl">
        {#if selectedIndex === i && data.digitalTwin}
          <tab.component 
            bind:this={tabRefs[i]}
            digitalTwin={data.digitalTwin} 
            digitalTwinId={data.id} 
          />
        {/if}
      </div>
    {/each}
  </div>
</div>
{/if}

<!-- Unsaved Changes Modal -->
<UnsavedChangesModal
  bind:show={showUnsavedChangesModal}
  currentTabName={tabs[selectedIndex]?.label || ''}
  targetTabName={
    pendingTabIndex !== null 
      ? tabs[pendingTabIndex]?.label || '' 
      : pendingNavigation?.navigation?.to?.url?.href || pendingNavigation?.navigation?.to || pendingNavigation?.url 
        ? getDestinationName(pendingNavigation.navigation?.to?.url?.href || pendingNavigation.navigation?.to || pendingNavigation.url || '')
        : 'een andere pagina'
  }
  on:saveAndContinue={handleSaveAndContinue}
  on:continueWithoutSaving={handleContinueWithoutSaving}
  on:cancel={handleCancel}
/>
