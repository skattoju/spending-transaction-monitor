import { Logo } from "../logo/logo";

export function Footer() {
  return (
    <footer className="mt-10">
      <div className="rounded-2xl border bg-card/60 p-4 text-xs text-muted-foreground backdrop-blur sm:flex sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <Logo />
          <span className="font-medium text-foreground">
            Built with the <span className="font-bold">AI Kickstart CLI</span>
          </span>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-3 sm:mt-0">
          <a className="hover:underline" href="#">
            Docs
          </a>
          <a className="hover:underline" href="#">
            GitHub
          </a>

        </div>
      </div>
    </footer>
  );
}