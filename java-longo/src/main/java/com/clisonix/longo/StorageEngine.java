package com.clisonix.longo;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

public class StorageEngine {
    private final Path storageFile;

    public StorageEngine(Path storageFile) {
        this.storageFile = storageFile;
    }

    public LongoCluster loadOrCreate() {
        if (!Files.exists(storageFile)) {
            return new LongoCluster();
        }
        try (ObjectInputStream in = new ObjectInputStream(new FileInputStream(storageFile.toFile()))) {
            Object obj = in.readObject();
            if (obj instanceof LongoCluster) {
                return (LongoCluster) obj;
            }
            return new LongoCluster();
        } catch (IOException | ClassNotFoundException e) {
            return new LongoCluster();
        }
    }

    public void save(LongoCluster cluster) throws IOException {
        Path parent = storageFile.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        try (ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(storageFile.toFile()))) {
            out.writeObject(cluster);
        }
    }
}
