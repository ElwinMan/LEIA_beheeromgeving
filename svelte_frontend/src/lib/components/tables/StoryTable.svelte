<script lang="ts">
  import type { Story } from '$lib/types/tool';
  import UpdateStoryModal from '$lib/components/modals/UpdateStoryModal.svelte';
  import { deleteStory } from '$lib/api';

  export let stories: Story[] = [];

  let modalComponent: any;

  function handleOpenModal(story: Story) {
    modalComponent.showModal(story);
  }

  async function handleDelete(storyId: number) {
    if (confirm('Weet je zeker dat je deze story wilt verwijderen?')) {
      try {
        await deleteStory(String(storyId));
        stories = stories.filter(s => s.id !== storyId);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<Story>) {
    const updatedStory = event.detail;
    const idx = stories.findIndex(s => s.id === updatedStory.id);
    if (idx > -1) {
      stories[idx] = updatedStory;
      stories = [...stories];
    }
  }
</script>

<UpdateStoryModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">Naam</th>
            <th class="bg-base-200 font-bold">Beschrijving</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each stories as story}
            <tr>
              <td>{story.name}</td>
              <td>{story.description}</td>
              <td class="relative">
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-40 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(story)} class="flex items-center gap-2">
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button class="text-error" on:click={() => handleDelete(story.id)}>
                        Verwijderen
                      </button>
                    </li>
                  </ul>
                </details>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      
      <!-- Add padding at the bottom for dropdown space -->
      <!-- Temp fix till dropdown fix for absolute position -->
      <div class="h-32"></div>

      {#if stories.length === 0}
        <div class="py-12 text-center opacity-70">Geen stories gevonden.</div>
      {/if}
    </div>
  </div>
</div>