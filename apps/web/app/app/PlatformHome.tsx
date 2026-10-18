'use client';

import Link from 'next/link';
import { useState } from 'react';
import { ArrowUpRight, Search, Waves, FileText, Globe, Brain, Activity, Network, Code2, Database, Users, Compass } from 'lucide-react';
import styles from './platform-home.module.css';

const tools = [
  { name: 'Ocean AI', group: 'Intelligence', icon: Waves, href: '/modules/curiosity-ocean', description: 'Ask questions, explore ideas and work with your documents.' },
  { name: 'Web Reader', group: 'Research', icon: Globe, href: '/modules/web-reader', description: 'Read websites and explore the information behind your sources.' },
  { name: 'Research Archive', group: 'Research', icon: Compass, href: '/modules/archive', description: 'Explore publications, references and scientific knowledge.' },
  { name: 'Trinity Debate', group: 'Intelligence', icon: Users, href: '/debate', description: 'Examine a question through multiple perspectives.' },
  { name: 'Zürich Engine', group: 'Intelligence', icon: Brain, href: '/zurich', description: 'Explore structured reasoning and analytical workflows.' },
  { name: 'EEG Analysis', group: 'Neuroscience', icon: Activity, href: '/modules/eeg-analysis', description: 'Open the workspace for brainwave and signal analysis.' },
  { name: 'Neural Synthesis', group: 'Neuroscience', icon: Brain, href: '/modules/neural-synthesis', description: 'Explore neural signal processing and synthesis tools.' },
  { name: 'My Data', group: 'Workspace', icon: Database, href: '/modules/my-data-dashboard', description: 'Access your data workspace and connected information.' },
  { name: 'Kloud Bridge', group: 'Infrastructure', icon: Network, href: '/modules/kloud-bridge', description: 'Inspect connectivity, containers and live infrastructure telemetry.' },
  { name: 'Developer Center', group: 'Infrastructure', icon: Code2, href: '/developers', description: 'Explore APIs, integration guides and developer resources.' },
];

export default function PlatformHome({ onReports }: { onReports: () => void }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const visible = tools.filter(tool => (category === 'All' || category === tool.group) && `${tool.name} ${tool.description}`.toLowerCase().includes(query.toLowerCase()));
  return <div className={styles.page}>
    <header className={styles.header}>
      <Link href="/" className={styles.brand}><span className={styles.logo}>C<span /></span>CLISONIX<span className={styles.platform}>PLATFORM</span></Link>
      <nav aria-label="Main navigation"><Link href="/modules">All modules</Link><Link href="/status">System status</Link><Link href="/modules/account" className={styles.account}>My account <ArrowUpRight size={15} /></Link></nav>
    </header>
    <main className={styles.main}>
      <section className={styles.hero}>
        <div><p className={styles.eyebrow}><span /> YOUR CONNECTED WORKSPACE</p><h1>From a question<br />to your next <em>creation.</em></h1><p className={styles.intro}>Think with Ocean. Explore knowledge. Turn your sources into documents and bring your work together in Clisonix.</p><div className={styles.actions}><Link href="/modules/curiosity-ocean" className={styles.primary}>Open Ocean AI <ArrowUpRight size={18} /></Link><button onClick={onReports} className={styles.secondary}>Create a report <FileText size={17} /></button></div><p className={styles.caption}>Intelligence · Research · Documents · Neuroscience · Infrastructure</p></div>
        <div className={styles.launchpad}><div className={styles.launchHeading}><span>START SOMETHING</span><span>01 — 03</span></div><Link href="/modules/curiosity-ocean"><Waves /><div><strong>Explore an idea</strong><p>Start a conversation with Ocean</p></div><ArrowUpRight /></Link><button onClick={onReports}><FileText /><div><strong>Produce a document</strong><p>PDF, Excel, Word or presentation</p></div><ArrowUpRight /></button><Link href="/modules/archive"><Globe /><div><strong>Find your next insight</strong><p>Open the research archive</p></div><ArrowUpRight /></Link><div className={styles.launchFooter}>One platform. Multiple ways to work.</div></div>
      </section>
      <section className={styles.directory} aria-labelledby="tools-title"><div className={styles.sectionHeading}><div><p className={styles.eyebrow}>EXPLORE CLISONIX</p><h2 id="tools-title">Your tools. Within reach.</h2></div><label className={styles.search}><Search size={18} /><input aria-label="Search tools" placeholder="Find a tool…" value={query} onChange={e => setQuery(e.target.value)} /></label></div>
        <div className={styles.filters} aria-label="Filter tools">{['All', ...Array.from(new Set(tools.map(t => t.group)))].map(group => <button key={group} aria-pressed={category === group} onClick={() => setCategory(group)}>{group}</button>)}</div>
        <div className={styles.grid}>{visible.map(tool => <Link key={tool.name} href={tool.href} className={styles.card}><div className={styles.cardTop}><span className={styles.icon}><tool.icon size={23} /></span><ArrowUpRight size={19} /></div><span className={styles.group}>{tool.group}</span><h3>{tool.name}</h3><p>{tool.description}</p><span className={styles.open}>Open workspace →</span></Link>)}</div>
        {!visible.length && <div role="status" className={styles.empty}>No tools match your search. <button onClick={() => { setQuery(''); setCategory('All'); }}>Clear filters</button></div>}
        <Link href="/modules" className={styles.all}>Browse the full module directory <ArrowUpRight size={17} /></Link>
      </section>
      <section className={styles.bottom}><div><Network size={26} /><h2>Connected through Kloud.</h2><p>Explore the infrastructure behind your workspace, with live telemetry and service monitoring.</p></div><Link href="/modules/kloud-bridge">Open infrastructure <ArrowUpRight size={18} /></Link></section>
    </main><footer className={styles.footer}><strong>CLISONIX</strong><span>Your intelligence workspace.</span><Link href="/status">Service status</Link></footer>
  </div>;
}
