import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// Tree components
const PREFIX_MIDDLE = '├── ';
const PREFIX_LAST = '└── ';
const PREFIX_PARENT_MIDDLE = '│   ';
const PREFIX_PARENT_LAST = '    ';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('dir-tree-gen.generateTree', async (uri: vscode.Uri) => {
        if (!uri || !uri.fsPath) {
            vscode.window.showErrorMessage('Please right-click on a folder to generate a directory tree');
            return;
        }

        const folderPath = uri.fsPath;
        const options = {
            showHidden: false,
            dirsOnly: false,
            depthLimit: 0
        };

        // Show quick pick for options
        const showHidden = await vscode.window.showQuickPick(
            ['Show hidden files', 'Hide hidden files'],
            { placeHolder: 'Show hidden files?' }
        );
        options.showHidden = showHidden === 'Show hidden files';

        const dirsOnly = await vscode.window.showQuickPick(
            ['Files and folders', 'Folders only'],
            { placeHolder: 'Include files or folders only?' }
        );
        options.dirsOnly = dirsOnly === 'Folders only';

        const depth = await vscode.window.showInputBox({
            prompt: 'Maximum depth (0 for unlimited)',
            value: '0',
            validateInput: value => {
                return isNaN(Number(value)) ? 'Please enter a number' : null;
            }
        });

        if (depth === undefined) {
            return; // User cancelled
        }

        options.depthLimit = parseInt(depth, 10) || 0;

        try {
            const tree = generateTree(folderPath, options);
            const doc = await vscode.workspace.openTextDocument({
                content: tree,
                language: 'plaintext'
            });
            await vscode.window.showTextDocument(doc);
        } catch (error) {
            vscode.window.showErrorMessage(`Error generating directory tree: ${error}`);
        }
    });

    context.subscriptions.push(disposable);
}

interface TreeOptions {
    showHidden: boolean;
    dirsOnly: boolean;
    depthLimit: number;
}

function generateTree(directory: string, options: TreeOptions): string {
    const name = path.basename(directory);
    let output = `${name}\n`;
    
    try {
        const { dirCount, fileCount } = generateTreeHelper(
            directory,
            '',
            1,
            options.depthLimit > 0 ? options.depthLimit : undefined,
            options.showHidden,
            options.dirsOnly
        );

        output += '\n';
        if (!options.dirsOnly) {
            output += `${dirCount} ${dirCount === 1 ? 'directory' : 'directories'}, `;
            output += `${fileCount} ${fileCount === 1 ? 'file' : 'files'}`;
        } else {
            output += `${dirCount} ${dirCount === 1 ? 'directory' : 'directories'}`;
        }
    } catch (error) {
        output += `\nError: ${error}`;
    }

    return output;
}

function generateTreeHelper(
    directory: string,
    prefix: string,
    level: number,
    limitDepth: number | undefined,
    showHidden: boolean,
    dirsOnly: boolean
): { dirCount: number; fileCount: number } {
    if (limitDepth !== undefined && level > limitDepth) {
        return { dirCount: 0, fileCount: 0 };
    }

    let dirCount = 0;
    let fileCount = 0;

    try {
        const items = fs.readdirSync(directory, { withFileTypes: true });
        const filteredItems = items.filter(item => {
            if (!showHidden && item.name.startsWith('.')) {
                return false;
            }
            if (dirsOnly && !item.isDirectory()) {
                return false;
            }
            return true;
        });

        filteredItems.sort((a, b) => a.name.localeCompare(b.name));

        for (let i = 0; i < filteredItems.length; i++) {
            const isLast = i === filteredItems.length - 1;
            const item = filteredItems[i];
            const itemPath = path.join(directory, item.name);
            const isDir = item.isDirectory();

            let line = prefix + (isLast ? PREFIX_LAST : PREFIX_MIDDLE) + item.name;
            console.log(line);

            if (isDir) {
                dirCount++;
                const newPrefix = prefix + (isLast ? PREFIX_PARENT_LAST : PREFIX_PARENT_MIDDLE);
                const { dirCount: subDirCount, fileCount: subFileCount } = generateTreeHelper(
                    itemPath,
                    newPrefix,
                    level + 1,
                    limitDepth,
                    showHidden,
                    dirsOnly
                );
                dirCount += subDirCount;
                fileCount += subFileCount;
            } else if (!dirsOnly) {
                fileCount++;
            }
        }
    } catch (error) {
        console.error(`Error processing directory ${directory}:`, error);
        throw error;
    }

    return { dirCount, fileCount };
}

export function deactivate() {}
