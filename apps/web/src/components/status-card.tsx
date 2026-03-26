type StatusCardProps = {
  title: string;
  value: string;
  description: string;
};

export function StatusCard({ title, value, description }: StatusCardProps) {
  return (
    <section className="glass p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
        {title}
      </p>
      <p className="mt-4 text-3xl font-semibold text-ink">{value}</p>
      <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
    </section>
  );
}

