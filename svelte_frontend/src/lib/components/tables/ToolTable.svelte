<script lang="ts">
	import { Settings, Database } from 'lucide-svelte';

	let { tools = [] } = $props();
</script>

<div class="card bg-base-100 shadow-xl">
	<div class="card-body p-0">
		<div class="overflow-x-auto">
			<table class="table table-xs table-pin-rows">
				<thead>
					<tr>
						<th class="bg-base-200 sticky font-bold w-full">Name</th>
						<th class="bg-base-200 font-bold text-right pr-10">Acties</th>
					</tr>
				</thead>
				<tbody>
					{#each tools as tool}
						<tr class="hover">
							<td class="text-sm font-bold w-full">{tool.name || '-'}</td>
							<td>
								<details class="dropdown dropdown-end text-right">
									<summary class="btn btn-sm btn-ghost">
										Opties
										<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
										</svg>
									</summary>
									<ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
										<li>
											<a 
												href={`/tools/${tool.id}`}
												class="flex items-center gap-2"
											>
												<Settings class="w-4 h-4" />
												Configureer tool
											</a>
										</li>
                                        <li>
                                            <a href={`/tools/${tool.id}/count`}>
                                                Tool gebruik overzicht
                                            </a>
                                        </li>
									</ul>
								</details>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			<!-- Extra ruimte voor dropdowns -->
			<div class="h-32"></div>

			{#if tools.length === 0}
				<div class="text-center py-12">
					<Database class="mx-auto h-12 w-12 opacity-50" />
					<h3 class="mt-2 text-lg font-medium">Geen tools</h3>
					<p class="mt-1 opacity-70">Er zijn nog geen tools beschikbaar.</p>
				</div>
			{/if}
		</div>
	</div>
</div>
