type Props = React.InputHTMLAttributes<HTMLInputElement> & { label: string };

export default function FormField({ label, ...props }: Props) {
  return (
    <label className="flex flex-col gap-1 text-sm text-gray-300">
      {label}
      <input
        {...props}
        className="rounded-lg bg-gray-900 border border-gray-700 px-3 py-2 text-gray-100 outline-none focus:border-indigo-500"
      />
    </label>
  );
}
