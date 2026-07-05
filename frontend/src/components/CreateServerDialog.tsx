import { useState } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Camera, Plus } from "lucide-react";
import { serversCreateServerMutation, serversGetMyServersOptions } from "@/client/@tanstack/react-query.gen.ts";
import useCustomToast from "@/hooks/useCustomToast.tsx";
import { handleError } from "@/utils";

interface CreateServerDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function CreateServerDialog({ open, onOpenChange }: CreateServerDialogProps) {
    const queryClient = useQueryClient();
    const { showSuccessToast, showErrorToast } = useCustomToast();

    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    const { mutate: createServer, isPending } = useMutation({
        ...serversCreateServerMutation(),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: serversGetMyServersOptions().queryKey });
            showSuccessToast("Server created");
            onOpenChange(false);
            setName("");
            setDescription("");
        },
        onError: handleError.bind(showErrorToast),
    });

    function handleSubmit() {
        if (!name.trim()) return;
        createServer({
            body: {
                name: name.trim(),
                description: description.trim() || null,
            }
        });
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="xs:max-w-md" style={{ backgroundColor: "var(--base)", border: "1px solid var(--surface1)" }}>
                <DialogHeader>
                    <DialogTitle className="text-xl text-center" style={{ color: "var(--text)" }}>Create Your Server</DialogTitle>
                    <p className="text-xs text-center" style={{ color: "var(--overlay1)" }}>
                        Give your server a name and personality. You can always change it later.
                    </p>
                </DialogHeader>

                <div className="flex flex-col items-center gap-5 py-2">
                    {/* Image upload zone — mocked */}
                    <button
                        className="relative w-20 h-20 rounded-full flex items-center justify-center border-2 border-dashed transition-colors hover:border-(--mauve)"
                        style={{ borderColor: "var(--surface2)", backgroundColor: "var(--surface0)" }}
                        disabled
                    >
                        <Camera size={24} style={{ color: "var(--overlay1)" }} />
                        <span
                            className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center"
                            style={{ backgroundColor: "var(--mauve)", color: "var(--base)" }}
                        >
                            <Plus size={12} />
                        </span>
                    </button>

                    {/* Name */}
                    <div className="w-full flex flex-col gap-1.5">
                        <Label className="text-xs font-semibold" style={{ color: "var(--text)" }}>
                            Server Name <span style={{ color: "var(--red)" }}>*</span>
                        </Label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                            placeholder="My awesome server"
                            maxLength={100}
                            className="text-sm"
                            style={{
                                backgroundColor: "var(--surface0)",
                                border: "1px solid var(--surface1)",
                                color: "var(--text)",
                            }}
                        />
                    </div>

                    {/* Description */}
                    <div className="w-full flex flex-col gap-1.5">
                        <Label className="text-xs font-semibold" style={{ color: "var(--text)" }}>
                            Description
                            <span className="ml-1 font-normal" style={{ color: "var(--overlay1)" }}>(optional)</span>
                        </Label>
                        <Textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="What's this server about?"
                            maxLength={300}
                            rows={3}
                            className="text-sm resize-none"
                            style={{
                                backgroundColor: "var(--surface0)",
                                border: "1px solid var(--surface1)",
                                color: "var(--text)",
                            }}
                        />
                        <span className="text-[10px] self-end" style={{ color: "var(--overlay1)" }}>
                            {description.length}/300
                        </span>
                    </div>
                </div>

                <div className="flex justify-between items-center pt-2">
                    <Button
                        variant="ghost"
                        onClick={() => onOpenChange(false)}
                        style={{ color: "var(--overlay1)" }}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={!name.trim() || isPending}
                        style={{ backgroundColor: "var(--mauve)", color: "var(--base)" }}
                    >
                        {isPending ? "Creating..." : "Create"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
