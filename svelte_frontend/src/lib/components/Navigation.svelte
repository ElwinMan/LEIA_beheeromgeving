<script lang="ts">
	import { page } from '$app/stores';
	import { Database, Layers, Wrench } from 'lucide-svelte';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();
	
	const navigationItems = [
		{ href: '/digital-twins', label: 'Digital Twins', icon: Database },
		{ href: '/layers', label: 'Layers', icon: Layers },
		{ href: '/tools', label: 'Tools', icon: Wrench }
	];
	
	function isActive(href: string) {
		return $page.url.pathname === href;
	}
</script>

<div class="drawer lg:drawer-open">
	<input id="drawer-toggle" type="checkbox" class="drawer-toggle" />
	
	<div class="drawer-content flex flex-col">
		<!-- Navbar for mobile -->
		<div class="navbar bg-base-100 lg:hidden">
			<div class="flex-none">
				<label for="drawer-toggle" class="btn btn-square btn-ghost">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
					</svg>
				</label>
			</div>
			<div class="flex-1">
				<span class="text-xl font-bold">LEIA Beheeromgeving</span>
			</div>
		</div>
		
		<!-- Page content slot -->
		<main class="flex-1 p-6">
			{@render children?.()}
		</main>
	</div>
	
	<div class="drawer-side">
		<label for="drawer-toggle" aria-label="close sidebar" class="drawer-overlay"></label>
		<aside class="bg-base-200 min-h-full w-80">
			<div class="p-4">
				<h1 class="text-xl font-bold mb-8 hidden lg:block">LEIA Beheeromgeving</h1>
				
				<ul class="menu p-0 space-y-2">
					{#each navigationItems as item}
						<li>
							<a
								href={item.href}
								class="flex items-center gap-3 {isActive(item.href) ? 'active' : ''}"
							>
								<item.icon class="w-5 h-5" />
								{item.label}
							</a>
						</li>
					{/each}
				</ul>
			</div>
		</aside>
	</div>
</div>
