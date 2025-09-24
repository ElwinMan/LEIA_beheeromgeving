<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    saveAndContinue: void;
    continueWithoutSaving: void;
    cancel: void;
  }>();

  export let show = false;
  export let currentTabName = '';
  export let targetTabName = '';

  let modalRef: HTMLDialogElement;

  $: if (show && modalRef) {
    modalRef.showModal();
  }

  function handleSaveAndContinue() {
    dispatch('saveAndContinue');
    close();
  }

  function handleContinueWithoutSaving() {
    dispatch('continueWithoutSaving');
    close();
  }

  function handleCancel() {
    dispatch('cancel');
    close();
  }

  function close() {
    show = false;
    modalRef?.close();
  }

  // Handle ESC key and backdrop click
  function handleClose() {
    handleCancel();
  }
</script>

<dialog bind:this={modalRef} class="modal" onclose={handleClose}>
  <div class="modal-box max-w-md">
    <div class="flex items-center gap-3 mb-4">
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center">
          <img src="/icons/alert-triangle.svg" alt="Waarschuwing" class="w-5 h-5 text-warning" />
        </div>
      </div>
      <div>
        <h3 class="font-bold text-lg">Niet opgeslagen wijzigingen</h3>
        <p class="text-sm text-base-content/70">
          Je hebt wijzigingen gemaakt in het tabblad "{currentTabName}"
        </p>
      </div>
    </div>

    <div class="mb-6">
      <p class="text-base-content/80">
        Wil je je wijzigingen opslaan voordat je naar "{targetTabName}" gaat?
      </p>
    </div>

    <div class="flex flex-col gap-3">
      <!-- Primary action - Save and continue -->
      <button 
        class="btn btn-primary w-full flex items-center justify-center gap-2" 
        onclick={handleSaveAndContinue}
      >
        <img src="/icons/save.svg" alt="Opslaan" class="w-4 h-4" />
        Opslaan en doorgaan
      </button>
      
      <!-- Secondary action - Continue without saving -->
      <button 
        class="btn btn-warning w-full flex items-center justify-center gap-2" 
        onclick={handleContinueWithoutSaving}
      >
        <img src="/icons/skip-forward.svg" alt="Doorgaan" class="w-4 h-4" />
        Doorgaan zonder opslaan
      </button>
      
      <!-- Cancel action -->
      <button 
        class="btn btn-ghost w-full flex items-center justify-center gap-2" 
        onclick={handleCancel}
      >
        <img src="/icons/x.svg" alt="Annuleren" class="w-4 h-4" />
        Annuleren
      </button>
    </div>
  </div>
  
  <!-- Backdrop -->
  <form method="dialog" class="modal-backdrop">
    <button onclick={handleCancel}>close</button>
  </form>
</dialog>