<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createTool } from '$lib/api';
  import type { Tool } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  let missingFields: string[] = [];

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Tool }>();

  let name: string = '';
  let description: string = '';
  let content: string | null = null;


  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorMessage: string = "Content moet geldig JSON zijn!";

  const jsonPlaceholder = `{
  "variable": "value",
  "variable2": "value2",
  "number1": 1,
  "array": [
    {"variableInArray": "value3"}
  ]
}`;

  function resetModal() {
    name = '';
    description = '';
    content = null;
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal() {
    resetModal();
    modalRef?.showModal();
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [
      { label: 'Naam', value: name }
    ];
    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    errorMessage = "Content moet geldig JSON zijn!";
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    let payload: any = {
      name,
      description,
      last_updated: new Date().toISOString()
    };

    if (typeof content === 'string' && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
        errorBanner?.hide?.();
      } catch (e) {
        errorBanner?.show();
        return;
      }
    } else {
      errorBanner?.hide?.();
    }

    try {
      const newTool = await createTool(payload);
      dispatch('created', newTool);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error: any) {
      // Check for duplicate name error (status 409 or message contains known phrases)
      if (
        error?.status === 409 ||
        (error?.message && (
          error.message.includes('duplicate key')
        ))
      ) {
        errorMessage = "Deze naam is al in gebruik. Kies een andere naam.";
      } else {
        errorMessage = "Content moet geldig JSON zijn!";
      }
      errorBanner?.show();
      console.error('Tool creation failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Tool succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message={errorMessage}
  />

  <form
    onsubmit={handleSubmit}
    class="modal-box w-full max-w-4xl space-y-4"
  >
    <div class="form-control">
      <h3 class="mb-4 text-lg font-bold">Nieuwe Tool Aanmaken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <div class="form-control">
      <label for="name" class="label font-semibold">
        Naam <span class="text-error">*</span>
        <HelpTooltip tip="De naam van de tool. Deze moet uniek zijn." position="right" />
      </label>
      <input id="name" class="input input-bordered w-full" bind:value={name} />
    </div>

    <div class="form-control">
      <label for="description" class="label font-semibold">
        Beschrijving
        <HelpTooltip tip="Een korte beschrijving van wat deze tool doet." position="right" />
      </label>
      <input id="description" class="input input-bordered w-full" bind:value={description} placeholder="Beschrijf wat deze tool doet..." />
    </div>

    <div class="form-control">
      <label for="content" class="label font-semibold">
        Content:
        <HelpTooltip tip="De configuratie van de tool in JSON formaat. Dit veld is optioneel." position="right" />
      </label>
      <textarea
        id="content"
        class="textarea textarea-bordered w-full min-h-[12rem]"
        bind:value={content}
        rows="10"
        placeholder={jsonPlaceholder}
      ></textarea>
    </div>

    <div class="flex justify-end gap-2 pt-4">
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>