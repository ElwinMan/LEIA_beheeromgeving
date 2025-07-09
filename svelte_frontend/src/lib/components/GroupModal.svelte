<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Group } from '$lib/types/group';
  import { createGroup } from '$lib/api';

  export let availableGroups: Group[] = [];
  export let digitalTwinId: number;
  let modalRef: HTMLDialogElement;

  let title = '';
  let parentId: number | null = null;

  const dispatch = createEventDispatcher();

  export function showModal() {
    title = '';
    parentId = null;
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    try {
      const newGroup = await await createGroup(digitalTwinId, {
        title,
        parent_id: parentId,
        digital_twin_id: digitalTwinId,
        });
      dispatch('created', newGroup);
      modalRef.close();
    } catch (error) {
      // Optionally show error
      console.error('Failed to create group', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box w-full max-w-md space-y-4">
    <h3 class="text-lg font-bold">Nieuwe groep aanmaken</h3>
    <label class="block">
      <span class="font-semibold">Naam groep:</span>
      <input class="input input-bordered w-full mt-1" bind:value={title} required />
    </label>
    <label class="block">
      <span class="font-semibold">Bovenliggende groep (optioneel):</span>
      <select class="select select-bordered w-full mt-1" bind:value={parentId}>
        <option value={null}>Geen (rootgroep)</option>
        {#each availableGroups as group}
          <option value={group.id}>{group.title}</option>
        {/each}
      </select>
    </label>
    <div class="flex justify-end gap-2 mt-4">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>