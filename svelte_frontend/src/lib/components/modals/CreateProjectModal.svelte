<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createProject } from '$lib/api';
  import type { Project } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Project }>();

  let name = '';
  let description = '';
  let content = '';

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const jsonPlaceholder = `{
  "key": "value",
  "anotherKey": 123,
  "array": [
    { "itemKey": "itemValue" }
  ]
}`;

  export function showModal() {
    name = '';
    description = '';
    content = '';
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    let payload: any = { name, description };
    if (content && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
      } catch (e) {
        errorBanner?.show();
        return;
      }
    }

    try {
      const newProject = await createProject(payload);
      dispatch('created', newProject);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Project creation failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Project succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Content moet geldig JSON zijn!"
  />

  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuw Project Aanmaken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <label for="content" class="pr-4 text-right font-semibold">Content (JSON):</label>
    <textarea
      id="content"
      class="textarea textarea-bordered col-span-3 w-full min-h-[12rem]"
      bind:value={content}
      rows="10"
      placeholder={jsonPlaceholder}
    ></textarea>
    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>