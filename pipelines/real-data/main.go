package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"
)

type Task struct {
	ID       string
	Domain   string
	Payload  map[string]any
	Metadata Metadata
}

type Metadata struct {
	Source    string
	RiskLevel string
	Timestamp time.Time
}

type CollectedData struct {
	Task        Task
	Raw         []byte
	ContentType string
	CollectedAt time.Time
}

type AnalyzedData struct {
	Task       Task
	Content    string
	Domain     string
	RiskLevel  string
	Provenance map[string]any
	ErrorRate  string
}

type ValidationResult struct {
	Status       string // PASS | SOFT_FAIL | HARD_FAIL
	Gaps         []string
	FixedContent string
}

type ValidatedData struct {
	Data       AnalyzedData
	Validation ValidationResult
}

type PublishRequest struct {
	TaskID     string
	ArticleID  string
	Source     string
	Domain     string
	Content    string
	Metadata   map[string]any
	Validation ValidationResult
}

type notifyEvent struct {
	Level   string
	Stage   string
	TaskID  string
	Message string
}

type auditOptions struct {
	PythonBin  string
	ScriptPath string
	ErrorRate  string
}

func main() {
	var (
		sourceURL       = flag.String("source-url", "", "Real HTTP source URL for collector")
		domain          = flag.String("domain", "", "Domain tag for this task")
		articleID       = flag.String("article-id", "", "Article ID for blog_publisher mode")
		publisherSource = flag.String("publisher-source", "dr_albana", "Source for blog_publisher mode: blerina or dr_albana")
		riskLevel       = flag.String("risk-level", "medium", "Risk level metadata")
		errorRate       = flag.String("error-rate", "", "Measured error rate for medical audit (ratio or percent according to script defaults)")
		publishEndpoint = flag.String("publish-endpoint", "", "Real publish API endpoint (required)")
		publishMode     = flag.String("publish-mode", "blog_publisher", "Publish mode: blog_publisher or raw")
		notifyEndpoint  = flag.String("notify-endpoint", "", "Optional notify webhook endpoint")
		pythonBin       = flag.String("python-bin", defaultPythonBin(), "Python executable path used for audit script")
		auditScript     = flag.String("audit-script", "scripts/audit_medical_gen_layers.py", "Path to real audit script")
		timeoutSec      = flag.Int("timeout-sec", 120, "Pipeline timeout seconds")
		collectWorkers  = flag.Int("collect-workers", 2, "Collector workers")
		analyzeWorkers  = flag.Int("analyze-workers", 2, "Analyzer workers")
		validateWorkers = flag.Int("validate-workers", 2, "Validator workers")
		publishWorkers  = flag.Int("publish-workers", 1, "Publisher workers")
	)
	flag.Parse()

	if strings.TrimSpace(*sourceURL) == "" {
		log.Fatal("--source-url is required (real data source)")
	}
	if strings.TrimSpace(*domain) == "" {
		log.Fatal("--domain is required")
	}
	if strings.TrimSpace(*errorRate) == "" {
		log.Fatal("--error-rate is required")
	}
	if strings.TrimSpace(*publishEndpoint) == "" {
		log.Fatal("--publish-endpoint is required (real publish target)")
	}
	if *publishMode != "blog_publisher" && *publishMode != "raw" {
		log.Fatal("--publish-mode must be one of: blog_publisher, raw")
	}
	if *publishMode == "blog_publisher" {
		if strings.TrimSpace(*articleID) == "" {
			log.Fatal("--article-id is required when --publish-mode=blog_publisher")
		}
		if *publisherSource != "blerina" && *publisherSource != "dr_albana" {
			log.Fatal("--publisher-source must be blerina or dr_albana for blog_publisher mode")
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(*timeoutSec)*time.Second)
	defer cancel()

	tasksIn := make(chan Task, 100)
	collectedCh := make(chan CollectedData, 100)
	analyzedCh := make(chan AnalyzedData, 100)
	validatedCh := make(chan ValidatedData, 100)
	publishCh := make(chan PublishRequest, 100)

	revalidateCh := make(chan AnalyzedData, 100)
	validatedFinalCh := make(chan ValidatedData, 100)
	notifyCh := make(chan notifyEvent, 100)

	auditCfg := auditOptions{
		PythonBin:  *pythonBin,
		ScriptPath: *auditScript,
		ErrorRate:  *errorRate,
	}

	client := &http.Client{Timeout: 30 * time.Second}

	var collectWG sync.WaitGroup
	for i := 0; i < *collectWorkers; i++ {
		collectWG.Add(1)
		go collectorWorker(ctx, i, tasksIn, collectedCh, notifyCh, client, &collectWG)
	}
	go func() {
		collectWG.Wait()
		close(collectedCh)
	}()

	var analyzeWG sync.WaitGroup
	for i := 0; i < *analyzeWorkers; i++ {
		analyzeWG.Add(1)
		go analyzerWorker(ctx, i, collectedCh, analyzedCh, notifyCh, &analyzeWG)
	}
	go func() {
		analyzeWG.Wait()
		close(analyzedCh)
	}()

	var validateWG sync.WaitGroup
	for i := 0; i < *validateWorkers; i++ {
		validateWG.Add(1)
		go validatorWorker(ctx, i, analyzedCh, validatedCh, notifyCh, auditCfg, false, &validateWG)
	}
	go func() {
		validateWG.Wait()
		close(validatedCh)
	}()

	var rewriterWG sync.WaitGroup
	rewriterWG.Add(1)
	go autoRewriterWorker(ctx, validatedCh, revalidateCh, notifyCh, auditCfg, &rewriterWG)
	go func() {
		rewriterWG.Wait()
		close(revalidateCh)
	}()

	var validateFinalWG sync.WaitGroup
	for i := 0; i < *validateWorkers; i++ {
		validateFinalWG.Add(1)
		go validatorWorker(ctx, i+1000, revalidateCh, validatedFinalCh, notifyCh, auditCfg, false, &validateFinalWG)
	}
	go func() {
		validateFinalWG.Wait()
		close(validatedFinalCh)
	}()

	var routerWG sync.WaitGroup
	routerWG.Add(1)
	go routerWorker(validatedFinalCh, publishCh, notifyCh, &routerWG)
	go func() {
		routerWG.Wait()
		close(publishCh)
	}()

	var publisherWG sync.WaitGroup
	for i := 0; i < *publishWorkers; i++ {
		publisherWG.Add(1)
		go publisherWorker(ctx, i, publishCh, notifyCh, client, *publishEndpoint, *publishMode, &publisherWG)
	}

	var notifierWG sync.WaitGroup
	notifierWG.Add(1)
	go notifierWorker(ctx, notifyCh, client, *notifyEndpoint, &notifierWG)

	task := Task{
		ID:     firstNonEmpty(*articleID, fmt.Sprintf("task-%d", time.Now().UnixNano())),
		Domain: *domain,
		Payload: map[string]any{
			"source_url":       *sourceURL,
			"error_rate":       *errorRate,
			"article_id":       firstNonEmpty(*articleID, ""),
			"publisher_source": *publisherSource,
			"publish_mode":     *publishMode,
			"publish_endpoint": *publishEndpoint,
		},
		Metadata: Metadata{
			Source:    *sourceURL,
			RiskLevel: *riskLevel,
			Timestamp: time.Now().UTC(),
		},
	}

	select {
	case tasksIn <- task:
		close(tasksIn)
	case <-ctx.Done():
		log.Fatal("context canceled before sending task")
	}

	publisherWG.Wait()
	close(notifyCh)
	notifierWG.Wait()

	if ctx.Err() != nil {
		log.Fatalf("pipeline timeout/cancelled: %v", ctx.Err())
	}

	log.Println("pipeline completed")
}

func collectorWorker(
	ctx context.Context,
	workerID int,
	in <-chan Task,
	out chan<- CollectedData,
	notifyCh chan<- notifyEvent,
	client *http.Client,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for task := range in {
		select {
		case <-ctx.Done():
			return
		default:
		}

		sourceURL, _ := task.Payload["source_url"].(string)
		if strings.TrimSpace(sourceURL) == "" {
			sourceURL = task.Metadata.Source
		}
		if strings.TrimSpace(sourceURL) == "" {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "collector", TaskID: task.ID, Message: "missing source URL"}
			continue
		}

		req, err := http.NewRequestWithContext(ctx, http.MethodGet, sourceURL, nil)
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "collector", TaskID: task.ID, Message: err.Error()}
			continue
		}

		resp, err := client.Do(req)
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "collector", TaskID: task.ID, Message: err.Error()}
			continue
		}

		raw, readErr := io.ReadAll(resp.Body)
		_ = resp.Body.Close()
		if readErr != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "collector", TaskID: task.ID, Message: readErr.Error()}
			continue
		}
		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "collector", TaskID: task.ID, Message: fmt.Sprintf("source HTTP %d", resp.StatusCode)}
			continue
		}

		out <- CollectedData{
			Task:        task,
			Raw:         raw,
			ContentType: resp.Header.Get("Content-Type"),
			CollectedAt: time.Now().UTC(),
		}

		notifyCh <- notifyEvent{Level: "INFO", Stage: "collector", TaskID: task.ID, Message: fmt.Sprintf("worker=%d bytes=%d", workerID, len(raw))}
	}
}

func analyzerWorker(
	ctx context.Context,
	workerID int,
	in <-chan CollectedData,
	out chan<- AnalyzedData,
	notifyCh chan<- notifyEvent,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for collected := range in {
		select {
		case <-ctx.Done():
			return
		default:
		}

		content := strings.TrimSpace(string(collected.Raw))
		if content == "" {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "analyzer", TaskID: collected.Task.ID, Message: "empty collected content"}
			continue
		}

		h := sha256.Sum256(collected.Raw)
		hash := hex.EncodeToString(h[:])

		analyzed := AnalyzedData{
			Task:      collected.Task,
			Content:   content,
			Domain:    collected.Task.Domain,
			RiskLevel: collected.Task.Metadata.RiskLevel,
			ErrorRate: toString(collected.Task.Payload["error_rate"]),
			Provenance: map[string]any{
				"source":         collected.Task.Metadata.Source,
				"content_type":   collected.ContentType,
				"byte_size":      len(collected.Raw),
				"sha256":         hash,
				"collected_at":   collected.CollectedAt.Format(time.RFC3339),
				"analyzed_at":    time.Now().UTC().Format(time.RFC3339),
				"analyzerWorker": workerID,
			},
		}

		out <- analyzed
		notifyCh <- notifyEvent{Level: "INFO", Stage: "analyzer", TaskID: collected.Task.ID, Message: fmt.Sprintf("worker=%d domain=%s", workerID, analyzed.Domain)}
	}
}

func validatorWorker(
	ctx context.Context,
	workerID int,
	in <-chan AnalyzedData,
	out chan<- ValidatedData,
	notifyCh chan<- notifyEvent,
	auditCfg auditOptions,
	rewrite bool,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for data := range in {
		select {
		case <-ctx.Done():
			return
		default:
		}

		result, err := runMedicalAudit(ctx, data.Content, data.ErrorRate, auditCfg, rewrite)
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "validator", TaskID: data.Task.ID, Message: err.Error()}
			result = ValidationResult{Status: "HARD_FAIL", Gaps: []string{err.Error()}}
		}

		out <- ValidatedData{Data: data, Validation: result}
		notifyCh <- notifyEvent{Level: "INFO", Stage: "validator", TaskID: data.Task.ID, Message: fmt.Sprintf("worker=%d status=%s", workerID, result.Status)}
	}
}

func autoRewriterWorker(
	ctx context.Context,
	in <-chan ValidatedData,
	out chan<- AnalyzedData,
	notifyCh chan<- notifyEvent,
	auditCfg auditOptions,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for validated := range in {
		select {
		case <-ctx.Done():
			return
		default:
		}

		switch validated.Validation.Status {
		case "PASS":
			out <- validated.Data
		case "SOFT_FAIL":
			res, err := runMedicalAudit(ctx, validated.Data.Content, validated.Data.ErrorRate, auditCfg, true)
			if err != nil {
				notifyCh <- notifyEvent{Level: "ERROR", Stage: "auto-rewriter", TaskID: validated.Data.Task.ID, Message: err.Error()}
				continue
			}
			if strings.TrimSpace(res.FixedContent) != "" {
				validated.Data.Content = res.FixedContent
			}
			out <- validated.Data
			notifyCh <- notifyEvent{Level: "INFO", Stage: "auto-rewriter", TaskID: validated.Data.Task.ID, Message: "rewrite attempted"}
		case "HARD_FAIL":
			notifyCh <- notifyEvent{Level: "WARN", Stage: "auto-rewriter", TaskID: validated.Data.Task.ID, Message: "hard fail routed to review"}
		default:
			notifyCh <- notifyEvent{Level: "WARN", Stage: "auto-rewriter", TaskID: validated.Data.Task.ID, Message: "unknown status"}
		}
	}
}

func routerWorker(
	in <-chan ValidatedData,
	publishCh chan<- PublishRequest,
	notifyCh chan<- notifyEvent,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for validated := range in {
		status := validated.Validation.Status
		if status == "PASS" || (status == "SOFT_FAIL" && strings.TrimSpace(validated.Validation.FixedContent) != "") {
			content := validated.Data.Content
			if strings.TrimSpace(validated.Validation.FixedContent) != "" {
				content = validated.Validation.FixedContent
			}

			publishCh <- PublishRequest{
				TaskID:    validated.Data.Task.ID,
				ArticleID: firstNonEmpty(toString(validated.Data.Task.Payload["article_id"]), validated.Data.Task.ID),
				Source:    firstNonEmpty(toString(validated.Data.Task.Payload["publisher_source"]), "dr_albana"),
				Domain:    validated.Data.Domain,
				Content:   content,
				Metadata: map[string]any{
					"risk_level": validated.Data.RiskLevel,
					"provenance": validated.Data.Provenance,
				},
				Validation: validated.Validation,
			}
			continue
		}

		notifyCh <- notifyEvent{
			Level:   "WARN",
			Stage:   "router",
			TaskID:  validated.Data.Task.ID,
			Message: fmt.Sprintf("blocked from publish: %s", status),
		}
	}
}

func publisherWorker(
	ctx context.Context,
	workerID int,
	in <-chan PublishRequest,
	notifyCh chan<- notifyEvent,
	client *http.Client,
	publishEndpoint string,
	publishMode string,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for req := range in {
		payload := map[string]any{}
		if publishMode == "blog_publisher" {
			payload = map[string]any{
				"article_id": req.ArticleID,
				"source":     req.Source,
			}
		} else {
			payload = map[string]any{
				"task_id":      req.TaskID,
				"domain":       req.Domain,
				"content":      req.Content,
				"metadata":     req.Metadata,
				"validation":   req.Validation,
				"published_at": time.Now().UTC().Format(time.RFC3339),
			}
		}
		body, err := json.Marshal(payload)
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "publisher", TaskID: req.TaskID, Message: err.Error()}
			continue
		}

		httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, publishEndpoint, bytes.NewReader(body))
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "publisher", TaskID: req.TaskID, Message: err.Error()}
			continue
		}
		httpReq.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(httpReq)
		if err != nil {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "publisher", TaskID: req.TaskID, Message: err.Error()}
			continue
		}
		respBody, _ := io.ReadAll(resp.Body)
		_ = resp.Body.Close()
		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			notifyCh <- notifyEvent{Level: "ERROR", Stage: "publisher", TaskID: req.TaskID, Message: fmt.Sprintf("HTTP %d: %s", resp.StatusCode, string(respBody))}
			continue
		}

		notifyCh <- notifyEvent{Level: "INFO", Stage: "publisher", TaskID: req.TaskID, Message: fmt.Sprintf("worker=%d publish success", workerID)}
	}
}

func notifierWorker(
	ctx context.Context,
	in <-chan notifyEvent,
	client *http.Client,
	notifyEndpoint string,
	wg *sync.WaitGroup,
) {
	defer wg.Done()
	for event := range in {
		log.Printf("[%s] stage=%s task=%s msg=%s", event.Level, event.Stage, event.TaskID, event.Message)

		if strings.TrimSpace(notifyEndpoint) == "" {
			continue
		}

		payload := map[string]any{
			"level":     event.Level,
			"stage":     event.Stage,
			"task_id":   event.TaskID,
			"message":   event.Message,
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		}
		body, err := json.Marshal(payload)
		if err != nil {
			log.Printf("[ERROR] notifier marshal: %v", err)
			continue
		}

		httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, notifyEndpoint, bytes.NewReader(body))
		if err != nil {
			log.Printf("[ERROR] notifier request: %v", err)
			continue
		}
		httpReq.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(httpReq)
		if err != nil {
			log.Printf("[ERROR] notifier call: %v", err)
			continue
		}
		_, _ = io.Copy(io.Discard, resp.Body)
		_ = resp.Body.Close()
	}
}

func runMedicalAudit(
	ctx context.Context,
	content string,
	errorRate string,
	auditCfg auditOptions,
	rewrite bool,
) (ValidationResult, error) {
	trimmed := strings.TrimSpace(content)
	if trimmed == "" {
		return ValidationResult{
			Status: "HARD_FAIL",
			Gaps:   []string{"empty_content"},
		}, nil
	}
	if strings.TrimSpace(errorRate) == "" {
		return ValidationResult{}, errors.New("missing error_rate for audit")
	}

	args := []string{
		auditCfg.ScriptPath,
		"--error-rate", errorRate,
		"--scan-doc-gaps",
	}
	if rewrite {
		args = append(args, "--rewrite-doc-gaps")
	}

	cmd := exec.CommandContext(ctx, auditCfg.PythonBin, args...)
	cmd.Env = os.Environ()
	stdout, err := cmd.Output()

	var exitErr *exec.ExitError
	if err != nil && !errors.As(err, &exitErr) {
		return ValidationResult{}, fmt.Errorf("audit execution failed: %w", err)
	}

	var payload map[string]any
	if unmarshalErr := json.Unmarshal(stdout, &payload); unmarshalErr != nil {
		return ValidationResult{}, fmt.Errorf("audit output parse failed: %w", unmarshalErr)
	}

	status := "HARD_FAIL"
	gaps := make([]string, 0)

	gateStatus := strings.ToUpper(toString(payload["status"]))
	if gateStatus == "PASS" {
		status = "PASS"
	}

	if protocol, ok := payload["clisonix_clisonix_document_protocol"].(map[string]any); ok {
		if failedFiles, exists := protocol["failed_files"].([]any); exists && len(failedFiles) > 0 {
			for _, f := range failedFiles {
				gaps = append(gaps, fmt.Sprintf("missing_sections:%v", f))
			}
			if status != "PASS" && !rewrite {
				status = "SOFT_FAIL"
			}
			if rewrite {
				status = "PASS"
			}
		}
	}

	if len(gaps) == 0 && status != "PASS" {
		gaps = append(gaps, "medical_gate_failed")
	}

	result := ValidationResult{
		Status:       status,
		Gaps:         gaps,
		FixedContent: "",
	}
	if rewrite && (status == "PASS" || status == "SOFT_FAIL") {
		result.FixedContent = content
	}

	return result, nil
}

func toString(v any) string {
	switch t := v.(type) {
	case string:
		return t
	case fmt.Stringer:
		return t.String()
	default:
		b, err := json.Marshal(t)
		if err != nil {
			return ""
		}
		return string(b)
	}
}

func defaultPythonBin() string {
	if fromEnv := strings.TrimSpace(os.Getenv("PYTHON_BIN")); fromEnv != "" {
		return fromEnv
	}
	return "python"
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			return value
		}
	}
	return ""
}
